import httpx
import trafilatura
from newspaper import Article
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL_NAME
import json

class ArticleSummarizer:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.system_prompt = """You are a strategic analyst and expert communicator. Your task is to distill complex articles into clear, insightful summaries for busy professionals who need to understand the core concepts and their implications quickly. Your analysis must go beyond surface-level points.For the provided article, produce the following:Core Thesis: In a single, precise sentence, articulate the author's central argument or primary claim.Key Arguments & Insights:•   Distill 3-5 of the most critical arguments, data points, or novel perspectives that support the core thesis.•   For each point, briefly explain its significance or implication. Focus on the "so what?" behind the information.•   Capture the author's reasoning, not just a list of topics. Avoid self-evident or generic statements.Strategic Takeaway: In one sentence, what is the single most important conclusion or strategic implication for the target audience?Audience & Relevance: In one sentence, describe the ideal reader for this article (e.g., by role, industry, or challenge) and the specific value they will gain from reading it.Guidelines:•   Length: Keep the total summary around 200-250 words.•   Focus: Prioritize depth and clarity over sheer brevity.•   Filtering: Eliminate marketing language, redundant examples, and introductory fluff, but retain the core logic and essential supporting details that give the article its weight."""

    def extract_article_text(self, url: str) -> str:
        try:
            client_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            with httpx.Client(timeout=15.0, headers=client_headers) as client:
                response = client.get(url, follow_redirects=True)
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

    def summarize_text(self, text: str) -> str:
        max_chars = 300000
        if len(text) > max_chars:
            text = text[:max_chars] + "..."
            print(f"📝 Truncated text to {max_chars} characters as a safeguard")
        
        try:
            print(f"🔄 Sending request to {GROQ_MODEL_NAME}")
            completion = self.client.chat.completions.create(
                model=GROQ_MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": f"{self.system_prompt}\n\nPlease analyze and summarize this article:\n\n{text}"
                    }
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None
            )
            return completion.choices[0].message.content
                    
        except Exception as e:
            print(f"❌ Exception during API call: {str(e)}")
            return f"❌ Summarization failed: {str(e)}"

    def process_url(self, url: str) -> str:
        try:
            print(f"🔍 Processing URL: {url}")
            
            article_text = self.extract_article_text(url)
            
            summary = self.summarize_text(article_text)
            
            return summary
            
        except Exception as e:
            error_msg = f"❌ Error processing article: {str(e)}"
            print(error_msg)
            return error_msg

if __name__ == '__main__':
    def test_summarizer():
        summarizer = ArticleSummarizer()
        test_url = "https://www.theverge.com/2023/10/26/23933428/meta-connect-2023-ray-ban-smart-glasses-vr-mixed-reality"
        
        try:
            summary = summarizer.process_url(test_url)
            print("\n--- FINAL SUMMARY ---\n")
            print(summary)
        except Exception as e:
            print(f"An error occurred: {e}")

    test_summarizer()