# [HuggingFace AI Agent Course] Unit 1. Introduction to Agents

# 개요

현재 페이지는https://huggingface.co/learn/agents-course/ko/unit1/introduction를 수강하고 제 방식으로 정리한 포스트입니다.

- **Unit 0. Welcome to the course**
- **Live 1. How the course works and Q&A**
- [**Unit 1. Introduction to Agents**](https://app.notion.com/p/HuggingFace-AI-Agent-Course-Unit-1-Introduction-to-Agents-36f13be817e5803d92d6d007eb103365?pvs=21)
- **Unit 2. Frameworks for AI Agents**
- **Unit 2.1 The smolagents framework**
- **Unit 2.2 The LlamaIndex framework**
- **Unit 2.3 The LangGraph framework**
- **Unit 3. Use Case for Agentic RAG**
- **Unit 4. Final Project - Create, Test, and Certify Your Agent**
- **Bonus Unit 1. Fine-tuning an LLM for Function-calling**
- **Bonus Unit 2. Agent Observability and Evaluation**
- **Bonus Unit 3. Agents in Games with Pokemon**

# 에이전트란?

우리가 자연어로 요청을 하면, 요청을 분석하여 추론과 계획을 통해 필요한 단계와 어떤 도구를 사용해야하는지 계획을 세웁니다. 예를들어 우리가 “커피 한잔 부탁해” 라고 요청하면 다음과 같이 에이전트는 계획과 도구를 선택합니다.

1. 사용자가 커피를 요청하고 있습니다. 인터넷에서 커피를 내리는 방법에 대해 찾아보겠습니다. 커피를 내리려면 커피 머신이 필요합니다. 커피 머신을 사용하는 방법에 대해서 찾아보겠습니다. 
2. 계획은 다음과 같습니다. 커피 머신을 사용해서 커피를 추출한다 → 커피를 잔에 담는다 → 사용자에게 커피를 제공한다.
3. 계획에 따라 수행하고 적절한 도구(커피머신)을 사용하여 사용자의 요청을 완료합니다.

![출처: huggingface](%5BHuggingFace%20AI%20Agent%20Course%5D%20Unit%201%20Introduction%20/image.png)

출처: huggingface

에이전트는 두 가지 주요 부분으로 나뉩니다.

1. 두뇌 (AI 모델)

사용자 요청을 분석해 추론과 계획을 처리하고 어떤 상황에 어떤 행동을 할지 결정을 내립니다. 보통 LLM이 두뇌 역할을 합니다.

1. 몸 (기능과 도구)

에이전트가 어떤 행동을 할 때, 어떤 도구를 사용해 처리하는 모든 작업들을 의미합니다.

# LLM이란?

LLM은 방대한 양의 텍스트 데이터를 학습하여 언어의 패턴, 구조, 뉘앙스를 익힌 AI 모델으로 사람의 언어를 이해하고 생성할 수 있습니다. 대부분의 현대 LLM은 트랜스포머(Transformer) 아키텍처를 기반으로 하는데, Google이 발표한 어텐션(Attention) 알고리즘을 사용한 딥러닝 아키텍처입니다.

트랜스포머는 3가지(인코더, 디코더, Seq2Seq) 유형이 있는데, 일반적으로 LLM은 수십억 개의 매개변수를 가진 디코더 기반 모델입니다. 상세히 다룰 내용은 아니지만 간단하게 말하면 디코더 기반 트랜스포머는 **한 번에 하나의 토큰을 생성하며 시퀀스를 완성**합니다. 

간단하면서 가장 효과적인 핵심 원리를 사용하는데, 바로 **이전 시퀀스를 기반으로 다음 토큰을 예측하는 방식**입니다. 여기서 말하는 토큰은 LLM 작업 정보 단위인데 특정 단어의 단위를 말합니다.

예를들어, interest와 ing라는 토큰을 결합하여 intersting을 만든거나 ed를 추가하여 interested를 만들 수 있는 것 처럼 말이죠.

![huggingface의 tokenizer playground 실습](%5BHuggingFace%20AI%20Agent%20Course%5D%20Unit%201%20Introduction%20/image%201.png)

huggingface의 tokenizer playground 실습

## EOS

LLM에는 모델별 고유한 특수 토큰이 존재하는데, LLM은 이 토큰들을 사용하여 생성하는 텍스트를 구조적으로 열고 닫습니다. 가장 중요한 것은 **EOS(End of Sequence)** 토큰인 **시퀀스 종료 토큰**입니다.

다음 표는 다양한 LLM의 특수 토큰을 보여줍니다.

| **모델** | **제공업체** | **EOS 토큰** | **기능** |
| --- | --- | --- | --- |
| **GPT4** | OpenAI | `<|endoftext|>` | 메시지 텍스트의 끝 |
| **Llama 3** | Meta (Facebook AI Research) | `<|eot_id|>` | 시퀀스의 끝 |
| **Deepseek-R1** | DeepSeek | `<|end_of_sentence|>` | 메시지 텍스트의 끝 |
| **SmolLM2** | Hugging Face | `<|im_end|>` | 지시 / 메시지의 끝 |
| **Gemma** | Google | `<end_of_turn>` | 대화 턴 끝 |

## 다음 토큰 예측

![출처: huggingface](%5BHuggingFace%20AI%20Agent%20Course%5D%20Unit%201%20Introduction%20/AutoregressionSchema.gif)

출처: huggingface

LLM은 자기 회귀 방식(즉, 이전 출력이 다음 입력이 되는 방식)으로 작동하는데, 이 과정이 계속 반복되고 모델이 다음 토큰으로 EOS 토큰을 예측하면 텍스트 생성을 중단하는 방식입니다.

텍스트 생성 과정을 기본적인 개요는 입력 테스트가 토큰화가 되면 모델은 각 토큰별로 다음 토큰이 될 가능성을 랭킹화하여 점수로 출력한다음, (여러 가지 방식이 있지만) 가장 간단한 방식으로 최대 점수가 높은 토큰을 선택하는 방식과 같이 다음 토큰을 선택합니다.

## Attention이 가장 중요하다

Transfomer 아키텍처에서 모든 단어가 동일한 중요도를 갖는게 아닙니다. “The capital of France is..” 문장에서 The, of, is 보다 capital, france가 가장 중요한 의미를 가집니다. 이것만으로도 프랑스의 수도 관련된 어떠한 요청으로 파악할 수 있는 중요한 키가 됩니다. 

그렇기 때문에 LLM에 어떻게 프롬프트를 입력하는지도 정말 중요합니다. 

LLM을 사용하다보면 컨텍스트 길이가 있는데 이건 LLM이 처리할 수 잇는 최대 토큰 수 이자, 모델의 최대 Attention Span을 의미합니다.

# 메시지와 특수 토큰

대화는 사용자와 LLM 간의 메시지로 이루어집니다. 사용자와 나눴던 대화를 기억하기 위해 LLM은 `채팅 템플릿`을 대화의 문맥을 유지하기 위해 사용합니다. 

예를들어 다음과 같이 대화를 했다면,

```python
conversation = [
    {"role": "user", "content": "나 주문하는 것 좀 도와줘."},
    {"role": "assistant", "content": "물론이지. 주문 번호 좀 알려줄래?"},
    {"role": "user", "content": "내 주문 번호는 ORDER-123야"},
]
```

LLM 마다 템플릿은 다릅니다. SmolLM2 채팅 템플릿은 conversation 리스트를 가지고 다음과 같은 프롬프트로 변환합니다.

```
<|im_start|>system
네 이름은 SmolLM이고, 도움을 주는 AI 어시스턴트로 Hugging Face로 훈련되었어.<|im_end|>
<|im_start|>user
나 주문하는 것 좀 도와줘.<|im_end|>
<|im_start|>assistant
물론이지. 주문 번호 좀 알려줄래?<|im_end|>
<|im_start|>user
내 주문 번호는 ORDER-123야<|im_end|>
<|im_start|>assistant
```

## 채팅 템플릿 (Chat-Templates)

채팅 템플릿은 LLM과 사용자의 대화를 특정 형식으로 구조화하는 역할을 합니다. 

LLM이 올바른 형식을 갖춘 대화를 수신하도록 하는 방법은 모델의 토크나이저가 제공하는 chat_template을 사용하면 됩니다.

```python
messages = [
    {"role": "system", "content": "너는 다양한 도구에 접근 가능한 AI 어시스턴트야."},
    {"role": "user", "content": "안녕!"},
    {"role": "assistant", "content": "안녕, 내가 어떻게 도와주면 될까?"},
]
```

이 대화를 아래와 같이 토크나이저를 불러와서 apply_chat_template을 호출하면 됩니다.

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-1.7B-Instruct")
rendered_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
```

최종 결과 값인 rendered_prompt는 모델에 입력으로 바로 사용 할 수 있습니다.

추가로 `apply_chat_template()` 함수는 ChatML 형식의 메시지를 처리할 때 API의 백엔드에서 사용됩니다.

# 도구 (Tool)

도구란 LLM에 제공하는 함수라고 할 수 있습니다. 일반적으로 사용하는 도구는 다음과 같습니다.

| **도구** | **설명** |
| --- | --- |
| 웹 검색 (Web Search) | 인터넷에서 최신 정보를 검색하여 가져옵니다. |
| 이미지 생성 (Image generation) | 주어진 설명을 기반으로 이미지를 생성합니다. |
| 정보 검색 (Retrieval) | 외부 데이터 소스에서 정보를 검색하여 제공합니다. |
| API 인터페이스 | 외부 API (GitHub, YouTube, Spotify 등)와 상호작용합니다. |

좋은 도구는 LLM의 능력을 보완할 수 있습니다. 예를 들어 LLM은 텍스트를 이해하고 텍스트로 응답을 내뱉습니다. 사용자가 이미지를 만들어달라고 했는데 이미지를 응답으로 내뱉을 수 없죠. 이때 **이미지 생성**이라는 **도구**를 사용하면 이 한계를 극복할 수 있습니다.

## 도구 작동 트리거

LLM은 텍스트를 출력할 수 있을 뿐 스스로 도구를 호출할 수 없습니다. LLM은 어떤 도구가 있고 어떤 상황에서 도구를 사용하고 도구를 사용할 때에는 도구 호출하는 텍스트를 생성하도록 하면, 에이전트가 도구 호출 텍스트를 파싱해서 실제 도구를 호출하는 역할을 수행합니다. 실제 도구를 호출한 것은 바로 에이전트입니다.

간단하게 예시를 통해 다음과 같이 도구를 구성합니다.

```python
@tool
def calculator(a: int, b: int) -> int:
    """두 정수를 곱하세요"""
    return a * b

print(calculator.to_string())
# Tool Name(도구명): calculator, Description(설명): Multiply two integers.(두 정수를 곱하세요), Arguments(인자): a: int, b: int, Outputs(출력): int
```

`@tool` 데코레이터는 to_string 함수를 제공합니다. to_string으로 생성된 도구에 대한 이름, 설명, 입력값, 출력값들에 대한 정보들이 시스템 프롬프트에 삽입되어 LLM이 필요에 따라 도구를 호출하도록 유도할 것 입니다.

# 에이전트: 사고-행동-관찰

에이전트는 사고(Thought) → 행동(Act) → 관찰(Observe)의 연속적인 주기로 작동합니다. 

1. 사고: 에이전트의 LLM이 다음 수행할 단계를 결정
2. 행동: 에이전트가 도구를 호출하는 등의 행동 수행
3. 관찰: LLM이 도구의 응답을 검토

에이전트는 위 주기를 while 루프를 사용하여 목표가 달성될 때까지 루프를 계속 실행합니다. 실제 에이전트 프레임워크마다는 정해둔 규칙과 가이드라인이 내장되어있으므로 해당 가이드라인을 따라 실행되게 됩니다.

실제 요청 예시를 살펴보면, 에이전트는 다음 스텝에 따라 수행됩니다.

> req: 뉴욕의 현재 날씨는 어때?
> 
1. 사고

사용자 질문에 에이전트는 다음과 같이 사고합니다. “사용자는 뉴욕의 현재 날씨 정보를 원한다. 날씨 API 호출 Tool이 있으니 이 도구를 통해 날씨 정보를 가져오자.”

1. 행동

뉴욕의 현재 날씨를 확인하기 위해 LLM은 다음과 같이 액션을 준비합니다.

```python
{
	 "action": "get_weather",
	 "action_input": {
		   "location": "New York"
	 }
}
```

1. 관찰

도구 호출 후 받은 결과는 추가 컨텍스트로 프롬프트에 더해진다음 피드백을 받습니다.

1. 사고

날씨 정보를 더한 프롬프트를 가지고 피드백을 요청하면, 다음과 같이 사고합니다. “뉴욕 현재 날씨 데이터를 확보했으니 사용자에게 정리해서 답변할 수 있어.”

1. 행동

사용자에게 지정된 형식에 맞게 응답을 생성합니다. “뉴욕의 현재 날씨는 부분적으로 흐리고, 기온과 습도는…” 최종 행동을 통해 답변을 하고 루프를 종료합니다.

## 사고: 에이전트의 내부 추론과 Re-Act 방식

에이전트는 작업을 해결하기 위해 내부적으로 추론하고 계획하는 과정을 거칩니다. 내부적으로 추론을 진행하면서 복잡한 문제를 더 작고 다루기 쉬운 단계로 분해하고 계획을 세웁니다.

아래는 일반적인 사고 유형의 예시입니다.

| **사고 유형** | **예시** |
| --- | --- |
| 계획 수립 | “이 작업을 세 단계로 나눠야겠다: 1) 데이터 수집, 2) 트렌드 분석, 3) 보고서 작성” |
| 분석 | “오류 메시지를 보니, 문제는 데이터베이스 연결 설정과 관련이 있는 것 같다” |
| 의사 결정 | “사용자의 예산 제약을 고려하면, 중간 가격대 옵션을 추천하는 것이 좋겠다” |
| 문제 해결 | “이 코드를 최적화하려면, 먼저 어디가 병목인지 프로파일링해봐야 한다” |
| 기억 활용 | “사용자가 앞서 파이썬을 선호한다고 했으니, 파이썬 예제를 제공해야겠다” |
| 자기 성찰 | “이전 접근법이 효과적이지 않았으니, 다른 방식을 시도해봐야겠다” |
| 목표 설정 | “이 작업을 완료하려면, 먼저 성공 기준을 명확히 해야 한다” |
| 우선순위 결정 | “새 기능을 추가하기 전에 보안 취약점부터 해결하는 것이 옳다” |
|  | 출처: huggingface |

### Re-Act 방식

핵심 방법론 중 하나는 추론 + 행동을 결합한 ReAct 방식입니다. ReAct는 LLM이 다음 토큰을 생성하기 전에 “단계별로 생각해보자”라는 문구를 추가하는 간단한 프롬프팅 기법입니다. 

모델에게 단계별로 생각하도록 지시하면, 계획을 세우는 방향으로 토큰 생성이 유도되기 때문에 복잡한 문제를 작게 쪼개서 작업할 수 있기 때문에 완성도 높은 답을 받을 수 있습니다. 우리가 실제 에이전트를 사용할 때에도 plan-mode를 통해 계획을 세우는 것도 이에 해당된다고 생각합니다.

## 액션: 에이전트 ↔ 환경 상호작용

액션은 에이전트가 정보를 위해 웹을 검색하는 것과 같은 의도적인 작업입니다. 

에이전트의 액션의 유형을 여러가지가 있는데 

| **에이전트 유형** | **설명** |
| --- | --- |
| JSON 에이전트 | 취할 액션이 JSON 형식으로 지정됩니다. |
| 코드 에이전트 | 에이전트가 외부에서 해석되는 코드 블록을 작성합니다. |
| 함수 호출 에이전트 | JSON 에이전트의 하위 카테고리로, 각 액션마다 새로운 메시지를 생성하도록 미세 조정되었습니다. |

액션은 여러 목적을 가질 수 있습니다. 

| **액션 유형** | **설명** |
| --- | --- |
| 정보 수집 | 웹 검색 수행, 데이터베이스 쿼리, 문서 검색 등 |
| 도구 사용 | API 호출, 계산 실행, 코드 실행 |
| 환경 상호작용 | 디지털 인터페이스 조작 또는 물리적 장치 제어 |
| 의사소통 | 채팅을 통한 사용자와의 상호작용 또는 다른 에이전트와의 협업 |

에이전트 유형 불문 가장 중요한 부분은 액션이 완료되면 새로운 토큰 생성을 중지하는 능력입니다. 이는 의도치 않은 출력 방지와 에이전트 응답의 퀄리티를 높여줍니다. 

### 중지 및 구문 분석 접근 방식

액션 구현 방법 중 하나는 **중지 및 구문 분석** **접근** **방식**입니다. 이 방법은 에이전트의 출력이 구조화되고 예측 가능을 보장합니다.

1. 구조화된 형식으로 생성

에이전트는 액션을 명확하고 정의된 형식(JSON | Code)으로 출력합니다.

1. 추가 생성 중지

액션이 완료되면 에이전트는 추가 토큰 생성을 중지합니다.

1. 출력 구문 분석

외부 파서가 형식화된 액션을 읽고 어떤 도구를 호출할지 결정하고 필요한 매개변수를 추출합니다. 날씨 확인 에이전트는 다음과 같이 출력할 수 있습니다.

```python
Thought: 서울의 현재 날씨를 확인해야 합니다.
Action :
{
  "action": "get_weather",
  "action_input": {"location": "Seoul"}
}
```

### 코드 에이전트

JSON 형식보다는 실행 가능한 코드 블럭을 생성하는 것이 더 나을 수 있습니다.

예를 들어 날씨 가져오는 액션을 코드 조각으로 나타내면 다음과 같습니다.

```python
# 코드 에이전트 예시: 날씨 정보 검색
def get_weather(city):
    import requests
    api_url = f"https://api.weather.com/v1/location/{city}?apiKey=YOUR_API_KEY"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get("weather", "날씨 정보가 없습니다")
    else:
        return "오류: 날씨 데이터를 가져올 수 없습니다."

# 함수 실행 및 최종 답변 준비
result = get_weather("Seoul")
final_answer = f"서울의 현재 날씨는: {result}"
print(final_answer)
```

API를 호출하여 날씨 데이터를 가져오고 구조화된 응답을 출력합니다. final_answer 출력하는 부분이 중지할 수 있는 플래그 역할을 합니다. 

JSON보다 코드 방식의 장점은 다음과 같습니다.

- 표현력: JSON에서는 할 수 없는 루프, 조건문, 함수 등과 같은 복잡한 로직 자것ㅇ
- 모듈성 및 재사용성: 함수와 모듈을 포함하여 재사용할 수 있음
- 디버깅: 프로그래밍 구문을 통해 코드 오류 감지 및 수정이 쉬움
- 직접 통합: 외부 API 및 라이브러리를 직접 통합하여 복잡한 작업 가능

## 관찰: 피드백을 통합하여 성찰 적응

관찰은 에이전트가 자신의 행동 결과를 인식하는 방법입니다. 

이 단계에서는 추가 사고 과정을 유도하고 행동으로 안내하는 중요한 정보를 제공합니다.

관찰 단계에서 에이전트는 다음과 같이 수행합니다.

- 피드백 수집: 행동이 성공했는지에 대한 데이터 및 확인
- 결과 추가: 새로운 정보를 기존 컨텍스트에 통합하여 메모리 업데이트
- 전략 조정: 업데이트 된 컨텍스트를 활용하여 이후 사고와 행동을 개선

예를 들어, 날씨 API 결과로 “구름 조금, *15°C, 습도 60%”*와 같은 데이터를 반환하면, 에이전트의 기억(프롬프트 끝 부분)에 추가됩니다. 이러한 피드백의 반복적 통합은 에이전트가 목표에 계속 맞춰 나가도록 보장할 수 있습니다. 

# smolagents로 첫 번째 에이전트 만들기

smolagents는 huggingface에서 제공해주는 에이전트 개발용 프레임워크입니다. 

```python
# Hub에서 도구 불러오기
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent = CodeAgent(
    model=model,
    tools=[final_answer, image_generation_tool], # 여기에 도구들을 추가하세요 (final_answer는 제거하지 마세요)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

GradioUI(agent).launch()
```

제공된 템플릿을 clone 한 다음, app.py에서 이미 선언된 image_generator tool을 추가하여 build 한 다음 고양이 이미지를 만들어달라고 요청해봤습니다.

![image.png](%5BHuggingFace%20AI%20Agent%20Course%5D%20Unit%201%20Introduction%20/image%202.png)

정상적으로 image_generator Tool 호출에 성공하여 final answer까지 완료된 것을 확인 할 수 있습니다.

# 수료증

![image.webp](%5BHuggingFace%20AI%20Agent%20Course%5D%20Unit%201%20Introduction%20/image.webp)