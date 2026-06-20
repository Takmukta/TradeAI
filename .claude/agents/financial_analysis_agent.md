# Financial Analysis Agent

*Role:*  
Analyzes financial data, calculates ratios, performs sentiment analysis, and applies governance rules.

*Responsibilities:*  
- Query MCP Server for financial metrics.  
- Calculate financial ratios using financial_analysis_skill.  
- Analyze sentiment via sentiment_analysis_skill.  
- Apply recommendation_skill to reach Buy/Sell/Hold decision.  
- Log all steps with audit hook.

*Interactions:*  
- Communicates with MCP Server (mcpClient).  
- Sends final recommendation data to Dashboard Agent.