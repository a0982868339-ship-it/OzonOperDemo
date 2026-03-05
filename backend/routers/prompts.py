"""
routers/prompts.py — 提示词工程 (Prompt Engineering) API

提供 Prompt 版本控制、在线沙盒调试、AI 自动优化 Prompt 的接口。
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.core.database import SessionLocal
from backend.models.prompt_template import PromptTemplate
from backend.services.model_provider_factory import ModelProviderFactory

router = APIRouter(prefix="/admin/prompts", tags=["prompts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Schemas ───────────────────────────────────────────────────────────────────

class PromptCreate(BaseModel):
    owner_agent:   str
    name:          str
    version:       str
    system_prompt: str
    user_template: str
    parameters:    Dict[str, Any]
    is_active:     bool = False


class PromptUpdate(BaseModel):
    name:          Optional[str] = None
    system_prompt: Optional[str] = None
    user_template: Optional[str] = None
    parameters:    Optional[Dict[str, Any]] = None


class SandboxRequest(BaseModel):
    system_prompt: str
    user_template: str
    parameters:    Dict[str, Any]
    variables:     Dict[str, str]  # Template variables to replace in user_template


class OptimizeRequest(BaseModel):
    description: str


def _serialize(p: PromptTemplate) -> dict:
    return {
        "id":            p.id,
        "owner_agent":   p.owner_agent,
        "name":          p.name,
        "version":       p.version,
        "system_prompt": p.system_prompt,
        "user_template": p.user_template,
        "parameters":    p.parameters,
        "is_active":     p.is_active,
        "created_at":    p.created_at.isoformat(),
        "updated_at":    p.updated_at.isoformat(),
    }


# ── CRUD ─────────────────────────────────────────────────────────────────────

@router.get("")
def list_prompts(db: Session = Depends(get_db)):
    """获取所有提示词模板（按 agent 和 version 排序）"""
    items = db.query(PromptTemplate).order_by(PromptTemplate.owner_agent, PromptTemplate.created_at.desc()).all()
    
    # Optional seed if empty
    if not items:
        seed = PromptTemplate(
            owner_agent="market_analyst",
            name="Ozon 选品分析师",
            version="v1.0",
            system_prompt="你是一位资深的俄罗斯 Ozon 电商选品专家，精通数据分析与市场洞察。",
            user_template="请分析以下商品：\n关键词: {{ keyword }}\n数据: {{ data }}",
            parameters={"temperature": 0.5, "max_tokens": 2048},
            is_active=True
        )
        db.add(seed)
        db.commit()
        db.refresh(seed)
        items = [seed]
        
    return [_serialize(i) for i in items]


@router.post("")
def create_prompt(body: PromptCreate, db: Session = Depends(get_db)):
    # Version constraint check
    exists = db.query(PromptTemplate).filter(
        PromptTemplate.owner_agent == body.owner_agent,
        PromptTemplate.version == body.version
    ).first()
    if exists:
        raise HTTPException(400, f"Version {body.version} already exists for agent {body.owner_agent}")

    if body.is_active:
        # Deactivate others
        db.query(PromptTemplate).filter(PromptTemplate.owner_agent == body.owner_agent).update({"is_active": False})
        
    p = PromptTemplate(
        owner_agent=body.owner_agent,
        name=body.name,
        version=body.version,
        system_prompt=body.system_prompt,
        user_template=body.user_template,
        parameters=body.parameters,
        is_active=body.is_active
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _serialize(p)


@router.put("/{prompt_id}")
def update_prompt(prompt_id: int, body: PromptUpdate, db: Session = Depends(get_db)):
    p = db.query(PromptTemplate).get(prompt_id)
    if not p:
        raise HTTPException(404, "Prompt not found")
        
    if body.name is not None: p.name = body.name
    if body.system_prompt is not None: p.system_prompt = body.system_prompt
    if body.user_template is not None: p.user_template = body.user_template
    if body.parameters is not None: p.parameters = body.parameters
    
    p.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(p)
    return _serialize(p)


@router.post("/{prompt_id}/activate")
def activate_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """设为线上生效版本"""
    p = db.query(PromptTemplate).get(prompt_id)
    if not p:
        raise HTTPException(404, "Prompt not found")
        
    db.query(PromptTemplate).filter(PromptTemplate.owner_agent == p.owner_agent).update({"is_active": False})
    p.is_active = True
    p.updated_at = datetime.utcnow()
    db.commit()
    
    return {"ok": True, "activated_id": prompt_id, "agent": p.owner_agent}


@router.delete("/{prompt_id}")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    p = db.query(PromptTemplate).get(prompt_id)
    if not p:
        raise HTTPException(404, "Prompt not found")
    if p.is_active:
        raise HTTPException(400, "Cannot delete active prompt version")
        
    db.delete(p)
    db.commit()
    return {"ok": True}


# ── Sandbox & Optimize ───────────────────────────────────────────────────────

@router.post("/sandbox")
async def run_sandbox(body: SandboxRequest, db: Session = Depends(get_db)):
    """在线运行测试给定的 Prompt"""
    # Replace variables in the user template
    user_prompt = body.user_template
    for key, val in body.variables.items():
        user_prompt = user_prompt.replace(f"{{{{ {key} }}}}", val).replace(f"{{{{{key}}}}}", val)
        
    try:
        # Use prompt_engineer's config for sandbox testing
        provider = ModelProviderFactory(db).get_provider("prompt_engineer")
        if not provider:
            # Fallback to orchestrator if prompt engineer is not configured
            provider = ModelProviderFactory(db).get_provider("orchestrator")
        if not provider:
            raise Exception("Please configure API key for 'prompt_engineer' or 'orchestrator' in Agent Configs first.")
            
        messages = [
            {"role": "system", "content": body.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        # We pass other parameters like temperature
        params_to_pass = {k:v for k,v in body.parameters.items() if k != "model_id"}
        
        start_time = datetime.utcnow()
        response_text = await provider.generate(messages, **params_to_pass)
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        
        # Estimate usage since we don't have token counts easily here
        est_tokens = (len(body.system_prompt) + len(user_prompt) + len(response_text)) // 3
        
        return {
            "result": response_text,
            "elapsed": round(elapsed, 2),
            "estimated_tokens": est_tokens
        }
    except Exception as e:
        raise HTTPException(500, f"Sandbox Error: {str(e)}")


@router.post("/optimize")
async def optimize_prompt(body: OptimizeRequest, db: Session = Depends(get_db)):
    """
    🪄 AI 魔法优化：根据简单描述自动生成高级结构化 Prompt 的接口。
    """
    meta_prompt = (
        "你是一个世界顶级的提示词工程师(Prompt Engineer)，精通大语言模型的工作原理和基于思维链(Chain of Thought)的结构化提示词编写。\\n"
        "你的任务是：根据用户的简单描述，帮其扩写生成一套具有『系统预设人设(System Prompt)』和『用户输入模版(User Template)』的高质量Prompt结构。\\n"
        "返回格式必须是 JSON，并且严格遵循以下字段：\\n"
        '{\\n'
        '  "system_prompt": "扮演的具体角色、核心能力和严格规则的详尽描述。分段落，使用Markdown格式",\\n'
        '  "user_template": "用户请求模板，你需要把核心变量抽取出来用 {{ 变量名 }} 占位，如：请分析 {{ keyword }}"\\n'
        '}'
    )
    
    try:
        provider = ModelProviderFactory(db).get_provider("prompt_engineer")
        if not provider:
            provider = ModelProviderFactory(db).get_provider("orchestrator")
        if not provider:
            raise Exception("请先在配置中设置 prompt_engineer 或 orchestrator 的大模型 Key")
            
        messages = [
            {"role": "system", "content": meta_prompt},
            {"role": "user", "content": f"帮我写一个提示词，描述需求：{body.description}"}
        ]
        
        response = await provider.generate(messages, temperature=0.7)
        
        # Extract JSON from potential markdown blocks ```json ... ```
        resp_clean = response.strip()
        if resp_clean.startswith("```json"):
            resp_clean = resp_clean.split("```json")[1]
        if resp_clean.startswith("```"):
            resp_clean = resp_clean.split("```")[1]
        if resp_clean.endswith("```"):
            resp_clean = resp_clean.rsplit("```", 1)[0]
            
        import json
        data = json.loads(resp_clean.strip())
        
        return {
            "system_prompt": data.get("system_prompt", ""),
            "user_template": data.get("user_template", "")
        }
    except Exception as e:
        raise HTTPException(500, f"Optimize Error: {str(e)}")
