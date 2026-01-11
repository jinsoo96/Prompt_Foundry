from typing import List, Dict
import json
import uuid
from app.models.schemas import GuidelineCompliance, ComplianceAnalysis
from app.services.llm_provider import get_default_llm


class ComplianceChecker:
    """시스템 프롬프트 준수도 검사 서비스"""

    def __init__(self):
        self.llm = get_default_llm()
        self.analysis_cache = {}  # 분석 결과 캐시

    def analyze_compliance(
        self,
        system_prompt_guidelines: List[str],
        user_message: str,
        assistant_response: str,
        llm_provider: str = None,
        model_name: str = None
    ) -> ComplianceAnalysis:
        """시스템 프롬프트 준수도 분석"""

        compliance_id = str(uuid.uuid4())

        # 모든 가이드라인을 한 번에 분석
        guideline_results = self._check_all_guidelines(
            guidelines=system_prompt_guidelines,
            user_message=user_message,
            assistant_response=assistant_response,
            llm_provider=llm_provider,
            model_name=model_name
        )

        # 전체 점수 계산
        followed_count = sum(1 for r in guideline_results if r.followed)
        overall_score = (followed_count / len(guideline_results) * 100) if guideline_results else 0

        # 요약 생성
        summary = self._generate_summary(guideline_results, overall_score)

        analysis = ComplianceAnalysis(
            compliance_id=compliance_id,
            overall_score=overall_score,
            guideline_results=guideline_results,
            summary=summary
        )

        # 캐시에 저장
        self.analysis_cache[compliance_id] = analysis

        return analysis

    def _check_all_guidelines(
        self,
        guidelines: List[str],
        user_message: str,
        assistant_response: str,
        llm_provider: str = None,
        model_name: str = None
    ) -> List[GuidelineCompliance]:
        """모든 가이드라인을 한 번에 분석"""

        if not guidelines:
            return []

        # LLM 선택
        from app.services.llm_provider import get_llm_provider
        if llm_provider:
            llm = get_llm_provider(llm_provider, model_name)
        else:
            llm = self.llm

        # 가이드라인 목록 생성
        guidelines_text = "\n".join([f"{i+1}. {g}" for i, g in enumerate(guidelines)])

        prompt = f"""Analyze if the assistant's response follows each guideline STRICTLY.

IMPORTANT RULES:
- If a guideline requires something (e.g., "use Chinese"), check if that thing is ACTUALLY PRESENT in the response
- If you cannot find CONCRETE EVIDENCE in the response, set followed=false
- Be STRICT: absence of required elements means the guideline was NOT followed
- Extract exact quotes as evidence whenever possible
- Write the "explanation" field in KOREAN (한글)

GUIDELINES:
{guidelines_text}

USER MESSAGE:
"{user_message}"

ASSISTANT RESPONSE:
"{assistant_response}"

For each guideline, determine if it was followed.
Return a JSON object with "results" array containing analysis for each guideline IN ORDER.
IMPORTANT: Write "explanation" in Korean.

Example format:
{{
  "results": [
    {{
      "guideline_index": 1,
      "followed": true,
      "explanation": "응답에 중국어가 포함되어 있어 가이드라인을 준수했습니다",
      "evidence": "你好，我可以帮助你"
    }},
    {{
      "guideline_index": 2,
      "followed": false,
      "explanation": "응답이 중국어가 아닌 영어로 작성되어 가이드라인을 준수하지 않았습니다",
      "evidence": "Hello, I can help you"
    }}
  ]
}}

Analyze each guideline carefully. Extract SPECIFIC EVIDENCE (quotes) from the response.
Write the explanation in Korean. If no evidence exists for a required element, set followed=false."""

        try:
            result_text = llm.chat(
                messages=[{"role": "user", "content": prompt}],
                json_format=True
            )
            print(f"Compliance check response: {result_text}")

            # JSON 파싱
            data = json.loads(result_text)
            results_data = data.get("results", [])

            # 결과를 GuidelineCompliance 객체로 변환
            results = []
            for i, guideline in enumerate(guidelines):
                # 해당 인덱스의 결과 찾기
                result_item = None
                for item in results_data:
                    if item.get("guideline_index") == i + 1:
                        result_item = item
                        break

                if result_item:
                    results.append(GuidelineCompliance(
                        guideline=guideline,
                        followed=result_item.get("followed", False),
                        explanation=result_item.get("explanation", "분석 실패"),
                        evidence=result_item.get("evidence")
                    ))
                else:
                    # 결과가 없는 경우
                    results.append(GuidelineCompliance(
                        guideline=guideline,
                        followed=False,
                        explanation="분석 결과를 찾을 수 없음",
                        evidence=None
                    ))

            return results

        except Exception as e:
            print(f"Compliance check error: {e}")
            # 에러 발생 시 모든 가이드라인에 대해 기본값 반환
            return [
                GuidelineCompliance(
                    guideline=g,
                    followed=False,
                    explanation=f"분석 중 오류 발생: {str(e)}",
                    evidence=None
                )
                for g in guidelines
            ]

    def _check_single_guideline(
        self,
        guideline: str,
        user_message: str,
        assistant_response: str
    ) -> GuidelineCompliance:
        """개별 가이드라인 준수 여부 체크 (레거시, 사용 안 함)"""

        # LLM을 사용하여 준수 여부 판단
        prompt = f"""다음은 시스템 프롬프트의 가이드라인입니다:
"{guideline}"

사용자 메시지:
"{user_message}"

어시스턴트 응답:
"{assistant_response}"

어시스턴트의 응답이 위 가이드라인을 따랐는지 분석해주세요.

다음 형식의 JSON으로만 응답해주세요:
{{
    "followed": true/false,
    "explanation": "판단 이유를 한 문장으로",
    "evidence": "응답에서 관련된 부분 (있다면)"
}}
"""

        try:
            result_text = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                json_format=True
            )

            # JSON 파싱
            try:
                result_data = json.loads(result_text)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 텍스트 분석
                result_data = self._fallback_parse(result_text)

            return GuidelineCompliance(
                guideline=guideline,
                followed=result_data.get("followed", False),
                explanation=result_data.get("explanation", "분석 실패"),
                evidence=result_data.get("evidence")
            )

        except Exception as e:
            # 에러 발생 시 기본값 반환
            return GuidelineCompliance(
                guideline=guideline,
                followed=False,
                explanation=f"분석 중 오류 발생: {str(e)}",
                evidence=None
            )

    def _fallback_parse(self, text: str) -> Dict:
        """JSON 파싱 실패 시 대체 파싱"""
        # 간단한 키워드 기반 분석
        followed = "true" in text.lower() or "따랐" in text or "준수" in text

        return {
            "followed": followed,
            "explanation": text[:100],  # 처음 100자만
            "evidence": None
        }

    def _generate_summary(
        self,
        guideline_results: List[GuidelineCompliance],
        overall_score: float
    ) -> str:
        """분석 요약 생성"""

        total = len(guideline_results)
        followed = sum(1 for r in guideline_results if r.followed)
        not_followed = total - followed

        summary = f"전체 {total}개 가이드라인 중 {followed}개를 준수했습니다 ({overall_score:.1f}%). "

        if not_followed > 0:
            not_followed_guidelines = [
                r.guideline for r in guideline_results if not r.followed
            ]
            summary += f"\n\n미준수 가이드라인:\n"
            for i, g in enumerate(not_followed_guidelines, 1):
                summary += f"{i}. {g}\n"

        return summary

    def get_analysis(self, compliance_id: str) -> ComplianceAnalysis:
        """캐시된 분석 결과 조회"""
        return self.analysis_cache.get(compliance_id)

    def extract_guidelines(self, system_prompt: str, llm_provider: str = None, model_name: str = None) -> List[str]:
        """LLM을 사용하여 시스템 프롬프트에서 가이드라인 추출"""
        from app.services.llm_provider import get_llm_provider

        # 지정된 LLM 사용, 없으면 기본값
        if llm_provider:
            llm = get_llm_provider(llm_provider, model_name)
        else:
            llm = self.llm

        prompt = f"""Extract specific guidelines from this system prompt.

System prompt:
"{system_prompt}"

Return ONLY a JSON object with a "guidelines" array containing each guideline as a string.
Each guideline should be a clear, actionable instruction.

Example output:
{{"guidelines": ["Respond in Chinese language", "Do not express emotions", "Be concise"]}}

Now extract guidelines from the given system prompt:"""

        try:
            result_text = llm.chat(
                messages=[{"role": "user", "content": prompt}],
                json_format=True
            )
            print(f"LLM response: {result_text}")  # 디버깅용

            # JSON 파싱
            try:
                data = json.loads(result_text)
                if isinstance(data, dict) and "guidelines" in data:
                    return [str(g).strip() for g in data["guidelines"] if g and len(str(g).strip()) > 3]
                elif isinstance(data, list):
                    return [str(g).strip() for g in data if g and len(str(g).strip()) > 3]
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}, text: {result_text}")

            return []

        except Exception as e:
            print(f"Guideline extraction error: {e}")
            return []
