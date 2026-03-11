import google.generativeai as genai
import asyncio
import logging
import os

logger = logging.getLogger('news_bot')

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = self._initialize_ai_model()

    def _initialize_ai_model(self):
        """환경 변수 GEMINI_API_KEY로 AI 모델 초기화"""
        if not self.api_key:
            logger.warning("경고: GEMINI_API_KEY가 설정되지 않았습니다. AI 요약 기능이 작동하지 않습니다.")
            return None
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("✓ Gemini 2.5 Flash 모델 초기화 완료.")
            return model
        except Exception as e:
            logger.error(f"✗ Gemini 모델 초기화 오류: {e}")
            return None

    async def summarize_with_ai(self, title, content):
        """AI로 뉴스 요약 (본문 내용 기반). 요청된 포맷을 따름."""
        if not self.model:
            return "AI 모델이 초기화되지 않아 요약할 수 없습니다."
            
        if not title or not content:
            return None
        
        max_length = 10000
        if len(content) > max_length:
            content = content[:max_length]
            
        try:
            prompt = f"""뉴스 내용을 아래 형식에 맞게 한국어로 요약해 주세요.

**요약 규칙:**
- 뉴스의 핵심만 2~3개 문단으로 요약합니다.
- 각 문단은 '>' 기호로 시작합니다.
- 문단과 문단 사이는 반드시 빈 줄 하나('> ')를 넣습니다.
- 다른 설명, 분석, 서론, 결론, 메타 정보 등은 절대 포함하지 않습니다.

**출력 형식:**
## **뉴스제목**
> 첫 번째 요약 문단
> 
> 두 번째 요약 문단
> 
> 세 번째 요약 문단(필요 시)

---
제목: {title}
내용: {content}
---
"""
            response = await asyncio.wait_for(
                self.model.generate_content_async(prompt),
                timeout=60.0
            )
            
            summary = response.text.strip()
            
            unwanted_phrases = [
                "물론입니다", "IT 전문 뉴스 에디터", "기사 내용을",
                "핵심만 담아", "전문적으로 요약", "---",
                "다음은", "요약입니다", "요약본입니다"
            ]
            
            lines = summary.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line_stripped = line.strip()
                if any(phrase in line_stripped for phrase in unwanted_phrases):
                    continue
                cleaned_lines.append(line)
            
            if cleaned_lines:
                return '\n'.join(cleaned_lines)
            
            return summary
            
        except asyncio.TimeoutError:
            logger.error("AI 요약 요청 시간 초과 (TimeoutError)")
            return f"오류: AI 요약 요청 시간 초과. 원문은 {title}."
        except Exception as e:
            logger.error(f"AI 요약 처리 중 오류: {e}")
            return None
