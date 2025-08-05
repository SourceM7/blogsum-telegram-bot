import httpx
import trafilatura
from newspaper import Article
import asyncio
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME
import json

class ArticleSummarizer:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        
        self.system_prompt = """You are a strategic analyst and expert communicator. Your task is to distill complex articles into clear, insightful summaries for busy professionals who need to understand the core concepts and their implications quickly. Your analysis must go beyond surface-level points.For the provided article, produce the following:Core Thesis: In a single, precise sentence, articulate the author's central argument or primary claim.Key Arguments & Insights:•   Distill 3-5 of the most critical arguments, data points, or novel perspectives that support the core thesis.•   For each point, briefly explain its significance or implication. Focus on the "so what?" behind the information.•   Capture the author's reasoning, not just a list of topics. Avoid self-evident or generic statements.Strategic Takeaway: In one sentence, what is the single most important conclusion or strategic implication for the target audience?Audience & Relevance: In one sentence, describe the ideal reader for this article (e.g., by role, industry, or challenge) and the specific value they will gain from reading it.Guidelines:•   Length: Keep the total summary around 200-250 words.•   Focus: Prioritize depth and clarity over sheer brevity.•   Filtering: Eliminate marketing language, redundant examples, and introductory fluff, but retain the core logic and essential supporting details that give the article its weight."""

    async def extract_article_text(self, url: str) -> str:
        try:
            client_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            async with httpx.AsyncClient(timeout=15.0, headers=client_headers) as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                extracted = trafilatura.extract(response.text)
                if extracted and len(extracted) > 200:
                    print(f"✅ Extracted {len(extracted)} characters using trafilatura")
                    return extracted
            
            article = Article(url)
            article.download()
            article.parse()
            
            if article.text and len(article.text) > 200:
                print(f"✅ Extracted {len(article.text)} characters using newspaper3k")
                return article.text
                
            raise Exception("Could not extract sufficient text from article")
            
        except Exception as e:
            raise Exception(f"Failed to extract article: {str(e)}")

    async def summarize_text(self, text: str) -> str:
        max_chars = 300000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            print(f"📝 Truncated text to {max_chars} characters as a safeguard")
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Please analyze and summarize this article:\n\n{text}"}
            ],
            "max_tokens": 800,
            "temperature": 0.3
        }
        
        try:
            print(f"🔄 Sending request to {MODEL_NAME}")
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                print(f"📡 API Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"📋 Full API Response: {json.dumps(result, indent=2)}")
                    
                    if "choices" in result and len(result["choices"]) > 0:
                        message = result["choices"][0]["message"]
                        content = message.get("content")
                        
                        if content:
                            print(f"✅ Generated summary ({len(content)} characters)")
                            return content.strip()
                        else:
                            error_msg = "❌ Could not find 'reasoning' or 'content' in the response message."
                            print(error_msg)
                            return error_msg
                    else:
                        print("❌ Unexpected response structure")
                        return f"❌ API returned unexpected response structure: {result}"
                else:
                    error_text = response.text
                    print(f"❌ API Error: {response.status_code} - {error_text}")
                    return f"❌ OpenRouter API error ({response.status_code}): {error_text}"
                    
        except Exception as e:
            print(f"❌ Exception during API call: {str(e)}")
            return f"❌ Summarization failed: {str(e)}"

    async def process_url(self, url: str) -> str:
        try:
            print(f"🔍 Processing URL: {url}")
            
            article_text = await self.extract_article_text(url)
            
            summary = await self.summarize_text(article_text)
            
            return summary
            
        except Exception as e:
            error_msg = f"❌ Error processing article: {str(e)}"
            print(error_msg)
            return error_msg

if __name__ == '__main__':
    async def test_summarizer():
        summarizer = ArticleSummarizer()
        test_url = "https://www.theverge.com/2023/10/26/23933428/meta-connect-2023-ray-ban-smart-glasses-vr-mixed-reality"
        
        try:
            summary = await summarizer.process_url(test_url)
            print("\n--- FINAL SUMMARY ---\n")
            print(summary)
        except Exception as e:
            print(f"An error occurred: {e}")

    asyncio.run(test_summarizer())