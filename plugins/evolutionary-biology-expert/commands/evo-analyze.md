# Analyze Evolutionary Biology Expert

Use the evolutionary biology expert agent to analyze a researcher's thought map, academic network, and research impact.

## Usage

```
/evo-analyze <expert_name> [research_topic]
```

## Arguments

- **expert_name** (required): The name of the evolutionary biology expert to analyze. Can be in English or Chinese.
- **research_topic** (optional): Specific research topic or area to focus the analysis on.

## Examples

```
/evo-analyze "Douglas Futuyma"
/evo-analyze "刘建全" "hybrid speciation"
/evo-analyze "James Mallet" "butterfly genomics"
```

## What it does

The agent will:

1. **Literature Analysis**: Search and analyze 30+ high-quality academic papers related to the expert
2. **Six-Dimension Framework**: Apply comprehensive analysis across:
   - Temporal dynamics analysis
   - Context-aware analysis  
   - Expert network analysis
   - Critical thinking analysis
   - Methodology analysis
   - Impact analysis

3. **Quality Control**: Ensure all literature meets strict standards (core journals ≥40%, relevance ≥0.6)

4. **Network Mapping**: Reconstruct academic collaboration networks and citation patterns

5. **Report Generation**: Produce a comprehensive analysis report with Nature-formatted citations

## Output

The analysis generates a detailed report including:
- Expert's academic thought map reconstruction
- Research trajectory and evolution patterns
- Collaboration network topology
- Critical assessment of theoretical contributions
- Standardized academic citations with PubMed links

## Requirements

This command requires the following MCP servers to be installed:
- article-mcp (for literature search)
- sequentialthinking (for structured analysis)
- mediawiki-mcp-server (for background information)
- playwright (for web analysis)

## Notes

- Analysis typically takes 5-10 minutes to complete
- All citations follow Nature journal format
- Results include critical perspectives and limitations
- Generated reports are saved for future reference