import asyncio
import os
from backend.services.collectors.ozon_collector import collect_ozon

raw = '''
is_cookies_accepted	1	www.ozon.ru	/	2026-04-04T13:58:45.190Z	20						Medium 
 __Secure-refresh-token	11.245766094.5R6nrY9JTQSPjc0tRC5bkw.78.AVnWC0WzhAitzR4e3yAu8uWPpio8aO7c56igqRoiL4KTemjbm4TPTxs54IXkdlX_WWyzBbg3D4IG928F1cquz8s0_rxLSFz1gzfWX5ILXdLNMHSKI4f3EASDTqXzL_C1E6XHvBYlUsx21JbL7wEmTnU.20260305135928.20260305155928.DYnDYkS1gwezPQaV2mXfxV0zvveAqSBLBk7lDfDQ9hs.13137dfc0ff2f3349	.ozon.ru	/	2027-03-05T13:59:28.185Z	304	✓	✓	Lax			Medium 
 __Secure-access-token	11.245766094.5R6nrY9JTQSPjc0tRC5bkw.78.AVnWC0WzhAitzR4e3yAu8uWPpio8aO7c56igqRoiL4KTemjbm4TPTxs54IXkdlX_WWyzBbg3D4IG928F1cquz8s0_rxLSFz1gzfWX5ILXdLNMHSKI4f3EASDTqXzL_C1E6XHvBYlUsx21JbL7wEmTnU.20260305135928.20260305155928.M9Z_cJBz31JadnkKJ0LHqXhrvdIMR4Lkn_UwTtPUzfk.12d6c208a9bc0ebfd	.ozon.ru	/	2027-03-05T13:59:28.185Z	303	✓	✓	Lax			Medium 
 __Secure-ext_xcid	1db7f28ab3be7b17c6382958c20035a6	.ozon.ru	/	2027-03-05T13:58:12.644Z	49	✓	✓	None			Medium 
 xcid	1db7f28ab3be7b17c6382958c20035a6	.ozon.ru	/	Session	36						Medium 
 __Secure-user-id	245766094	.ozon.ru	/	2027-03-05T13:59:28.186Z	25	✓	✓	Lax			Medium 
 abt_data	7.f-rLYc3wMbpNTOQBbo7TDRgea15eHMgLVHIXJLb6MsxmdUNK8j_U1H1tJi-GpS46i3v-I-t9Wlfar0ZKwqyqTfzTKhuF5_d0zt8bjTwEfPurvzuHcalIAbkKeQMIYkaLU-AUc-LfUzv_FoV0u_G_UpAf-6xA0RHhihAJuQRmkQEDdcqGJPASo5EBd4U9SrVzva-fr-dBJ5yepMwTTN9CVbqUpw0wtorXINEwypyE4Snkl5FZyCypcxJpL-LO2KAUZH2vCxWyAau8CvrO1KcHtDanFVwuSZY-xTthC0yPFr3tlqbigWSm28eF--R1nCi0_K-Q2u5H17nRv4CYrSdqL4TqThouRR7TQ6e8Fzi_eXymwsaGcoUZcLAhVOVut8f0PBHlwHLdLiKvKd9vj4TUcuiATwYbftcupXCFfnIjzuVAeMeaebgpbk8_8bzsQlImkB2Las3FN8_clyOfVe8Wqkwt8vVyM7uoXj-CE6Au0yLmc4qV8Ledj1zn9-1Iyz-LmRNl9fczIYU0cCUZwEea0ithySQu	.ozon.ru	/	2027-03-05T13:59:50.244Z	550	✓	✓	None	  		Medium 
 abt_data	7.w30q8ddihvsWQkWC9WkLNerLux852dJ0RnZedwYEag21x4kcQqSQqJpU6DHx-32pRpvdq6OuGVqUB0YMDr-6lrY5Yjpu_xaG_wveVLfP48VqDPSkMyuxGFRqWlJqxp7ygzpjIRXIhOaE8R4FSuTT0qmrAXWsB82njFBvr7B988KtuufMUiONTZ6HHpCZsMTP1QnycDWNOH5BEGDcyBlB_WLcTrSppt4jev7_Vpg7z7VYsyqyIm6tigL06LfE2qxRChWu-Temka9wjORKbBIV5UiheCYs-FmLZR_You8-Cp_-HJt1mqCPHnlyTImOnJaCp0rrTr5o1HRhAmds3PWyONdW4ABjpgDXYQ	.ozone.ru	/	2027-03-05T13:58:10.030Z	364	✓	✓	None	  	✓	Medium 
 __Secure-ab-group	78	.ozon.ru	/	2027-03-05T13:59:28.186Z	19		✓	Lax			Medium 
 rfuid	LTE5NTAyNjU0NzAsMTI0LjA0MzQ3NjU3ODA4MTAzLC0xNzcyNzUyODA1LC0xLDM2NTQxMTUyNixXM3NpYm1GdFpTSTZJbEJFUmlCV2FXVjNaWElpTENKa1pYTmpjbWx3ZEdsdmJpSTZJbEJ2Y25SaFlteGxJRVJ2WTNWdFpXNTBJRVp2Y20xaGRDSXNJbTFwYldWVWVYQmxjeUk2VzNzaWRIbHdaU0k2SW1Gd2NHeHBZMkYwYVc5dUwzQmtaaUlzSW5OMVptWnBlR1Z6SWpvaWNHUm1JbjBzZXlKMGVYQmxJam9pZEdWNGRDOXdaR1lpTENKemRXWm1hWGhsY3lJNkluQmtaaUo5WFgwc2V5SnVZVzFsSWpvaVEyaHliMjFsSUZCRVJpQldhV1YzWlhJaUxDSmtaWE5qY21sd2RHbHZiaUk2SWxCdmNuUmhZbXhsSUVSdlkzVnRaVzUwSUVadmNtMWhkQ0lzSW0xcGJXVlVlWEJsY3lJNlczc2lkSGx3WlNJNkltRndjR3hwWTJGMGFXOXVMM0JrWmlJc0luTjFabVpwZUdWeklqb2ljR1JtSW4wc2V5SjBlWEJsSWpvaWRHVjRkQzl3WkdZaUxDSnpkV1ptYVhobGN5STZJbkJrWmlKOVhYMHNleUp1WVcxbElqb2lRMmh5YjIxcGRXMGdVRVJHSUZacFpYZGxjaUlzSW1SbGMyTnlhWEIwYVc5dUlqb2lVRzl5ZEdGaWJHVWdSRzlqZFcxbGJuUWdSbTl5YldGMElpd2liV2x0WlZSNWNHVnpJanBiZXlKMGVYQmxJam9pWVhCd2JHbGpZWFJwYjI0dmNHUm1JaXdpYzNWbVptbDRaWE1pT2lKd1pHWWlmU3g3SW5SNWNHVWlPaUowWlhoMEwzQmtaaUlzSW5OMVptWnBlR1Z6SWpvaWNHUm1JbjFkZlN4N0ltNWhiV1VpT2lKTmFXTnliM052Wm5RZ1JXUm5aU0JRUkVZZ1ZtbGxkMlZ5SWl3aVpHVnpZM0pwY0hScGIyNGlPaUpRYjNKMFlXSnNaU0JFYjJOMWJXVnVkQ0JHYjNKdFlYUWlMQ0p0YVcxbFZIbHdaWE1pT2x0N0luUjVjR1VpT2lKaGNIQnNhV05oZEdsdmJpOXdaR1lpTENKemRXWm1hWGhsY3lJNkluQmtaaUo5TEhzaWRIbHdaU0k2SW5SbGVIUXZjR1JtSWl3aWMzVm1abWw0WlhNaU9pSndaR1lpZlYxOUxIc2libUZ0WlNJNklsZGxZa3RwZENCaWRXbHNkQzFwYmlCUVJFWWlMQ0prWlhOamNtbHdkR2x2YmlJNklsQnZjblJoWW14bElFUnZZM1Z0Wlc1MElFWnZjbTFoZENJc0ltMXBiV1ZVZVhCbGN5STZXM3NpZEhsd1pTSTZJbUZ3Y0d4cFkyRjBhVzl1TDNCa1ppSXNJbk4xWm1acGVHVnpJam9pY0dSbUluMHNleUowZVhCbElqb2lkR1Y0ZEM5d1pHWWlMQ0p6ZFdabWFYaGxjeUk2SW5Ca1ppSjlYWDFkLFd5SjZhQzFEVGlKZCwwLDEsMCwyNCwyMzc0MTU5MzAsOCwyMjcxMjY1MjAsMCwxLDAsLTQ5MTI3NTUyMyxSMjl2WjJ4bElFbHVZeTRnVG1WMGMyTmhjR1VnUjJWamEyOGdUV0ZqU1c1MFpXd2dOUzR3SUNoTllXTnBiblJ2YzJnN0lFbHVkR1ZzSUUxaFl5QlBVeUJZSURFd1h6RTFYemNwSUVGd2NHeGxWMlZpUzJsMEx6VXpOeTR6TmlBb1MwaFVUVXdzSUd4cGEyVWdSMlZqYTI4cElFTm9jbTl0WlM4eE5EVXVNQzR3TGpBZ1UyRm1ZWEpwTHpVek55NHpOaUF5TURBek1ERXdOeUJOYjNwcGJHeGgsZXlKamFISnZiV1VpT25zaVlYQndJanA3SW1selNXNXpkR0ZzYkdWa0lqcG1ZV3h6WlN3aVNXNXpkR0ZzYkZOMFlYUmxJanA3SWtSSlUwRkNURVZFSWpvaVpHbHpZV0pzWldRaUxDSkpUbE5VUVV4TVJVUWlPaUpwYm5OMFlXeHNaV1FpTENKT1QxUmZTVTVUVkVGTVRFVkVJam9pYm05MFgybHVjM1JoYkd4bFpDSjlMQ0pTZFc1dWFXNW5VM1JoZEdVaU9uc2lRMEZPVGs5VVgxSlZUaUk2SW1OaGJtNXZkRjl5ZFc0aUxDSlNSVUZFV1Y5VVQxOVNWVTRpT2lKeVpXRmtlVjkwYjE5eWRXNGlMQ0pTVlU1T1NVNUhJam9pY25WdWJtbHVaeUo5ZlgxOSw2NSwtMTE4MzQxMDcyLDEsMSwtMSwxNjk5OTU0ODg3LDE2OTk5NTQ4ODcsODE2OTMxNDUzLDg=	.ozon.ru	/	2026-03-06T13:58:14.000Z	2409						Medium 
 __Secure-ETC	d078bcd4c5530a413755e3d21a46fafc	.ozon.ru	/	2027-03-05T13:58:08.528Z	44	✓	✓	None			Medium 
 ozonIdAuthResponseToken	eyJhbGciOiJIUzI1NiIsIm96b25pZCI6Im5vdHNlbnNpdGl2ZSIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyNDU3NjYwOTQsImlzX3JlZ2lzdHJhdGlvbiI6ZmFsc2UsInJldHVybl91cmwiOiIiLCJwYXlsb2FkIjpudWxsLCJleHAiOjE3NzI3MTkxNzgsImlhdCI6MTc3MjcxOTE2OCwiaXNzIjoib3pvbmlkIn0.dge6eEMgCuZuGRaEeDo6fiGRJ-9B3CQM9Cd-cheIegU	www.ozon.ru	/	2026-03-05T21:59:39.248Z	303						Medium 
 guest	true	.ozon.ru	/	Session	9						Medium 
 is_adult_confirmed		.ozon.ru	/	Session	18						Medium 
 is_alco_adult_confirmed		.ozon.ru	/	Session	23						Medium 
 user_locale		.www.ozon.ru	/	Session	11						Medium
'''

pairs = []
for line in raw.strip().split('\n'):
    parts = line.strip().split()
    if len(parts) >= 2:
        pairs.append(f'{parts[0]}={parts[1]}')

os.environ['OZON_COOKIES'] = '; '.join(pairs)

async def run():
    print(f'Starting with {len(pairs)} cookies...')
    data = await collect_ozon()
    print(f'Count: {len(data)}')
    if data: print(data[0])

asyncio.run(run())
