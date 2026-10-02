import os
import json
import requests
from datetime import datetime, timedelta, timezone

# API Keys
API_KEY = os.environ.get("OPENDART_API_KEY")
KAKAO_REST_API_KEY = os.environ.get("KAKAO_REST_API_KEY")
KAKAO_REFRESH_TOKEN = os.environ.get("KAKAO_REFRESH_TOKEN")

KOSPI200_SECTORS = {
    "화학·에너지": ["LG화학", "S-Oil", "SK이노베이션", "롯데케미칼", "SK가스", "GS", "한국가스공사", "한화솔루션", "금호석유", "OCI홀딩스", "대한유화"],
    "이차전지·배터리": ["LG에너지솔루션", "POSCO홀딩스", "포스코퓨처엠", "삼성SDI", "엘앤에프", "에코프로머티", "코스모신소재", "포스코인터내셔널", "솔루스첨단소재", "금양"],
    "조선·해운·중공업": ["HD현대중공업", "한화오션", "삼성중공업", "HD한국조선해양", "한화엔진", "HD현대", "HD현대마린엔진", "HD현대마린솔루션", "대한조선", "한국카본", "HD현대미포", "HMM", "팬오션"],
    "전기·전자(반도체/IT)": ["삼성전자", "SK하이닉스", "삼성전기", "LG이노텍", "한미반도체", "LG전자", "이수페타시스", "DB하이텍", "삼성에스디에스", "LG디스플레이", "해성디에스"],
    "자동차·운송장비": ["현대차", "기아", "현대모비스", "현대오토에버", "현대글로비스", "현대위아", "에스엘", "HL만도", "한국타이어앤테크놀로지"],
    "원전·전력인프라": ["한국전력", "두산에너빌리티", "한전기술", "한전KPS", "효성중공업", "산일전기", "대한전선", "일진전기", "LS ELECTRIC", "HD현대일렉트릭", "LS에코에너지", "LS", "효성"],
    "방위산업·우주항공": ["한화에어로스페이스", "현대로템", "한국항공우주", "한화시스템", "LIG넥스원", "한화", "풍산"],
    "제약·바이오": ["삼성바이오로직스", "셀트리온", "유한양행", "한미약품", "SK바이오팜", "삼성에피스홀딩스", "녹십자", "대웅제약", "SK바이오사이언스", "종근당", "대원제약", "한올바이오파마"],
    "화장품·의류": ["아모레퍼시픽", "LG생활건강", "한국콜마", "코스맥스", "토니모리", "애경산업", "F&F", "영원무역"],
    "금융·지주": ["KB금융", "신한지주", "하나금융지주", "메리츠금융지주", "기업은행", "우리금융지주", "JB금융지주", "카카오뱅크", "카카오페이", "삼성물산", "SK"],
    "손해보험": ["삼성화재", "DB손해보험", "현대해상", "한화손해보험", "삼성화재우", "롯데손해보험", "서울보증보험", "삼성생명", "코리안리"],
    "증권사": ["삼성증권", "미래에셋증권", "한국금융지주", "키움증권", "SK증권", "NH투자증권", "한화투자증권", "현대차증권", "대신증권"],
    "인터넷·게임·플랫폼": ["NAVER", "카카오", "크래프톤", "엔씨소프트", "넷마블"],
    "건설·시공": ["현대건설", "대우건설", "GS건설", "DL이앤씨", "HDC현대산업개발"],
    "철강·금속": ["고려아연", "현대제철", "동국제강", "세아제강"],
    "음식료·유통": ["삼양식품", "CJ제일제당", "오리온", "농심", "BGF리테일", "이마트", "롯데쇼핑", "신세계", "하이트진로"]
}

KOSDAQ150_SECTORS = {
    "제약·바이오": ["알테오젠", "HLB", "삼천당제약", "리가켐바이오", "에스티팜", "HK이노엔", "동국제약", "지투지바이오", "디엔디파마텍", "올릭스", "에이비엘바이오", "펩트론", "오스코텍", "엘앤씨바이오", "셀트리온제약", "차바이오텍", "메디톡스", "보로노이", "지노믹트리"],
    "미용의료·화장품": ["휴젤", "클래시스", "실리콘투", "파마리서치", "제이시스메디칼", "원텍", "브이티", "아이패밀리에스씨", "마녀공장", "코스메카코리아"],
    "이차전지·소재": ["에코프로비엠", "에코프로", "엔켐", "대주전자재료", "서진시스템", "나노신소재", "피엔티", "동화기업", "한중엔시에스", "에코프로에이치엔", "성일하이텍", "더블유씨피", "윤성에프앤씨", "새빗켐"],
    "반도체 소부장": ["HPSP", "리노공업", "주성엔지니어링", "이오테크닉스", "솔브레인", "동진쎄미켐", "티씨케이", "ISC", "하나머티리얼즈", "대덕전자", "유진테크", "심텍", "원익IPS", "테크윙", "파크시스템스", "두산테스나", "팸텍", "씨엠티엑스", "원익QnC", "고영", "이녹스첨단소재"],
    "엔터·미디어": ["JYP Ent.", "에스엠", "스튜디오드래곤", "CJ ENM", "와이지엔터테인먼트", "디어유", "초록뱀미디어", "삼화네트웍스"],
    "게임·소프트웨어": ["펄어비스", "카카오게임즈", "위메이드", "넥슨게임즈", "컴투스", "네오위즈", "웹젠", "엠게임", "안랩"],
    "로봇·자동화": ["레인보우로보틱스", "로보티즈", "에스에프에이", "휴림로봇", "로보스타", "에스피지", "하이젠알앤엠", "삼현", "유일로보틱스", "티로보틱스", "에브리봇", "뉴로메카", "알에스오토메이션"],
    "피팅·배관기자재": ["성광벤드", "태광", "하이록코리아", "디케이락", "비엠티", "태웅"]
}

TARGET_MAP = {}
for sector, comps in KOSPI200_SECTORS.items():
    for c in comps:
        TARGET_MAP[c.strip()] = {"market": "KOSPI 200", "sector": sector}
for sector, comps in KOSDAQ150_SECTORS.items():
    for c in comps:
        TARGET_MAP[c.strip()] = {"market": "KOSDAQ 150", "sector": sector}


def get_kakao_access_token():
    """Refresh Token을 이용해 새로운 Access Token을 발급받습니다."""
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": KAKAO_REST_API_KEY,
        "refresh_token": KAKAO_REFRESH_TOKEN
    }
    resp = requests.post(url, data=data).json()
    return resp.get("access_token")

def send_kakao_message(access_token, corp_name, report_nm, url):
    """카카오톡 '나에게 보내기' API를 호출합니다."""
    send_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    template = {
        "object_type": "text",
        "text": f"🚨 [DART 신규공시]\n\n기업명: {corp_name}\n공시명: {report_nm}",
        "link": {
            "web_url": url,
            "mobile_web_url": url
        },
        "button_title": "공시 원문 보기"
    }
    data = {"template_object": json.dumps(template)}
    requests.post(send_url, headers=headers, data=data)


def fetch_disclosures_for_period(bgn_de, end_de):
    base_url = "https://opendart.fss.or.kr/api/list.json"
    matched_items = []
    page = 1

    while True:
        params = {
            "crtfc_key": API_KEY,
            "bgn_de": bgn_de,
            "end_de": end_de,
            "page_no": page,
            "page_count": 100
        }
        resp = requests.get(base_url, params=params, timeout=15)
        data = resp.json()

        if data.get("status") != "000":
            break

        disclosures = data.get("list", [])
        if not disclosures:
            break

        for item in disclosures:
            corp_name = item.get("corp_name", "").strip()
            if corp_name in TARGET_MAP:
                matched_items.append({
                    "rcept_no": item.get("rcept_no"),
                    "corp_name": corp_name,
                    "stock_code": item.get("stock_code", ""),
                    "report_nm": item.get("report_nm"),
                    "rcept_dt": item.get("rcept_dt"),
                    "flr_nm": item.get("flr_nm"),
                    "rm": item.get("rm", ""),
                    "market": TARGET_MAP[corp_name]["market"],
                    "sector": TARGET_MAP[corp_name]["sector"],
                    "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={item.get('rcept_no')}"
                })

        total_pages = data.get("total_page", 1)
        if page >= total_pages or page >= 15:
            break
        page += 1

    return matched_items


def main():
    if not API_KEY:
        raise ValueError("OPENDART_API_KEY 환경 변수가 설정되지 않았습니다.")

    # 💡 한국 시간(KST, UTC+9) 강제 설정
    KST = timezone(timedelta(hours=9))
    today = datetime.now(KST)

    bgn_de = (today - timedelta(days=5)).strftime("%Y%m%d")
    end_de = today.strftime("%Y%m%d")

    new_items = fetch_disclosures_for_period(bgn_de, end_de)

    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "disclosures.json")
    existing_items = []
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                existing_items = content.get("disclosures", [])
        except Exception:
            existing_items = []

    # 기존 데이터와 비교하여 '진짜 새로운 공시'만 필터링
    existing_ids = {item["rcept_no"] for item in existing_items}
    new_alerts = [item for item in new_items if item["rcept_no"] not in existing_ids]

    # 카카오톡 전송 로직
    if new_alerts and KAKAO_REST_API_KEY and KAKAO_REFRESH_TOKEN:
        try:
            k_token = get_kakao_access_token()
            if k_token:
                # 카톡 도배 방지를 위해 최대 5건까지만 전송
                for alert in new_alerts[:5]:
                    send_kakao_message(k_token, alert["corp_name"], alert["report_nm"], alert["url"])
                
                if len(new_alerts) > 5:
                    send_kakao_message(k_token, "대시보드 시스템", f"외 {len(new_alerts)-5}건의 신규 공시가 더 있습니다. 대시보드를 확인하세요.", "https://github.com")
        except Exception as e:
            print(f"Kakao Alert Error: {e}")

    # 데이터 병합 및 저장
    items_by_id = {item["rcept_no"]: item for item in existing_items}
    for item in new_items:
        items_by_id[item["rcept_no"]] = item

    merged_list = sorted(
        list(items_by_id.values()),
        key=lambda x: (x["rcept_dt"], x["rcept_no"]),
        reverse=True
    )[:500]

    # 💡 갱신 시간 기록 시에도 한국 시간(KST) 적용
    payload = {
        "updated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(merged_list),
        "disclosures": merged_list
    }

    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Update complete: {len(new_alerts)} new alerts sent. {len(merged_list)} disclosures recorded.")


if __name__ == "__main__":
    main()
