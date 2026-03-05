from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class ImageGenerationRequest(BaseModel):
    product_name: str
    material: str
    function: str
    scenario: str
    style: str
    size: str  # 1:1, 3:4
    copy_text: Optional[str] = None

class ImageGenerationResponse(BaseModel):
    task_id: str
    status: str
    image_urls: List[str]

class VideoGenerationRequest(BaseModel):
    description: str
    features: str
    scenario: str
    duration: int  # 15, 30, 60
    language: str  # 'ru', 'zh'

class VideoGenerationResponse(BaseModel):
    task_id: str
    status: str
    video_url: str
    cover_url: str

class CopywritingRequest(BaseModel):
    product_info: str
    selling_points: str
    platform: str
    language: str

class CopywritingResponse(BaseModel):
    seo_title: List[str]
    short_description: str
    detail_description: str
    ad_copy: str

from typing import Dict, Any

class SEORequest(BaseModel):
    product_name: str
    category: str

class SEOResponse(BaseModel):
    title_seo: str
    short_description: str
    bullet_points_ru: List[str]
    tags: List[str]

class MediaRequest(BaseModel):
    product_name: str
    description: str

class MediaResponse(BaseModel):
    image_prompt: str
    video_prompt: str
    urls: List[str]

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
