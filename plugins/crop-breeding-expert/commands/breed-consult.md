# Consult Crop Breeding Expert

Use the crop breeding expert agent to get professional guidance on breeding program design, molecular techniques, and variety improvement strategies.

## Usage

```
/breed-consult <crop_type> <breeding_goal> [method]
```

## Arguments

- **crop_type** (required): The target crop species (e.g., "wheat", "rice", "corn", "soybean").
- **breeding_goal** (required): The specific breeding objective:
  - "yield_improvement" - Increase yield potential
  - "disease_resistance" - Enhance disease resistance
  - "stress_tolerance" - Improve abiotic stress tolerance
  - "quality_enhancement" - Improve grain quality or nutritional traits
- **method** (optional): Preferred breeding approach:
  - "molecular" - Molecular breeding and marker-assisted selection
  - "genomic_selection" - Genomic selection approaches
  - "hybrid" - Hybrid breeding strategies
  - "conventional" - Traditional breeding methods

## Examples

```
/breed-consult "wheat" "disease_resistance" "molecular"
/breed-consult "rice" "yield_improvement" "genomic_selection"
/breed-consult "corn" "stress_tolerance" "hybrid"
```

## What it does

The agent will:

1. **Program Design**: Provide comprehensive breeding program design recommendations

2. **Technical Guidance**:
   - Breeding program design and timeline
   - Variety improvement strategies
   - Molecular breeding consultation

3. **Method Selection**: Recommend appropriate breeding techniques based on crop and goals

4. **Resource Planning**: Suggest required resources, timelines, and evaluation methods

## Output

The consultation provides:
- Detailed breeding program design
- Recommended molecular techniques and markers
- Selection strategy and evaluation criteria
- Timeline and resource requirements
- Risk assessment and mitigation strategies
- Relevant scientific literature and case studies

## Requirements

This command requires the following MCP servers:
- article-mcp (for crop science literature)
- genome-mcp (for genomic analysis and marker identification)

## Notes

- Integrates traditional breeding knowledge with modern molecular approaches
- Provides practical, actionable recommendations for current breeding programs
- Considers economic and logistical constraints
- Includes examples from successful breeding programs

## Specializations

- **Cereal crops**: Wheat, rice, corn, barley, sorghum
- **Legume crops**: Soybean, common bean, pea, lentil
- **Specialty crops**: Vegetables, fruits, industrial crops
- **Stress breeding**: Drought, heat, salinity, disease resistance