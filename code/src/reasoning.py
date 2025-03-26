from langchain.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def reason_about_breaks(breaks_df):
    from database import retrieve_similar_cases  # ⬅️ Move import inside the function
    
    llm = Ollama(model="gemma:latest")
    prompt_template = PromptTemplate(
        input_variables=["riskdate", "quantity_a", "quantity_b", "tolerance", "comment", "historical_cases"],
        template="""
        Given the following reconciliation break:
        - Risk Date: {riskdate}
        - Quantity System A: {quantity_a}
        - Quantity System B: {quantity_b}
        - Tolerance: {tolerance}
        - Comment: {comment}
        
        Historical similar cases:
        {historical_cases}
        
        Classify the break and suggest a resolution.keep it to 30 words
        """
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    responses = []
    for _, row in breaks_df.iterrows():
        historical_cases = retrieve_similar_cases(f"{row['riskdate']} {row['quantity_a']} {row['quantity_b']} {row['tolerance']} {row['comment']}")
        response = chain.run(
            riskdate=row['riskdate'],
            quantity_a=row['quantity_a'],
            quantity_b=row['quantity_b'],
            tolerance=row['tolerance'],
            comment=row['comment'],
            historical_cases=historical_cases
        )
        responses.append(response.strip())
    
    breaks_df["Resolution Suggestion"] = responses
    return breaks_df


def analyze_mismatch(riskdate, quantity_a, quantity_b, tolerance=0, comment=""):
    from database import retrieve_similar_cases  # Moved inside to avoid circular import

    llm = Ollama(model="gemma:latest")
    prompt_template = PromptTemplate(
        input_variables=["riskdate", "quantity_a", "quantity_b", "tolerance", "comment", "historical_cases"],
        template="""
        Given the following reconciliation break:
        - Risk Date: {riskdate}
        - Quantity System A: {quantity_a}
        - Quantity System B: {quantity_b}
        - Tolerance: {tolerance}
        - Comment: {comment}

        Historical similar cases:
        {historical_cases}

        Classify the break and suggest a resolution.
        """
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Retrieve historical similar cases using a query text
    query_text = f"{riskdate} {quantity_a} {quantity_b} {tolerance} {comment}"
    historical_cases = retrieve_similar_cases(query_text)

    response = chain.run(
        riskdate=riskdate,
        quantity_a=quantity_a,
        quantity_b=quantity_b,
        tolerance=tolerance,
        comment=comment,
        historical_cases=historical_cases
    )
    return response.strip()

