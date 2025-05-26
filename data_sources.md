# Data Sources for Country-Level Job Data

## Overview of Required Data
For creating job complexity and price indexes at the country level, we need the following types of data:
1. Occupational employment statistics
2. Occupational wage data
3. Task-level data for occupations
4. Industry-occupation matrices
5. Economic indicators for context

## United States
- **Bureau of Labor Statistics (BLS)**
  - Occupational Employment and Wage Statistics (OEWS): https://www.bls.gov/oes/
  - Current Employment Statistics (CES): https://www.bls.gov/ces/
  - Occupational Requirements Survey (ORS): https://www.bls.gov/ors/
- **O*NET Database**
  - Detailed task and skill data by occupation: https://www.onetonline.org/
- **Census Bureau**
  - American Community Survey (ACS): https://www.census.gov/programs-surveys/acs

## European Union
- **Eurostat**
  - European Labour Force Survey (EU-LFS): https://ec.europa.eu/eurostat/web/microdata/european-union-labour-force-survey
  - Structure of Earnings Survey (SES): https://ec.europa.eu/eurostat/web/microdata/structure-of-earnings-survey
- **European Skills, Competences, Qualifications and Occupations (ESCO)**
  - Occupation and skill classifications: https://esco.ec.europa.eu/en

## United Kingdom
- **Office for National Statistics (ONS)**
  - Annual Survey of Hours and Earnings (ASHE): https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/bulletins/annualsurveyofhoursandearnings/previousReleases
  - Labour Force Survey (LFS): https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/methodologies/labourforcesurveyuserguidance
- **UK Skills and Employment Survey**
  - Task and skill data: https://www.cardiff.ac.uk/research/explore/find-a-project/view/626669-skills-and-employment-survey-2017

## Canada
- **Statistics Canada**
  - Labour Force Survey (LFS): https://www.statcan.gc.ca/en/survey/household/3701
  - Job Vacancy and Wage Survey (JVWS): https://www.statcan.gc.ca/en/survey/business/5217
- **Employment and Social Development Canada (ESDC)**
  - National Occupational Classification (NOC): https://noc.esdc.gc.ca/

## Mexico
- **Instituto Nacional de Estadística y Geografía (INEGI)**
  - National Survey of Occupation and Employment (ENOE): https://www.inegi.org.mx/programas/enoe/15ymas/
- **Secretaría del Trabajo y Previsión Social (STPS)**
  - Mexican Occupational Information System: https://www.observatoriolaboral.gob.mx/

## India
- **Ministry of Statistics and Programme Implementation (MOSPI)**
  - Periodic Labour Force Survey (PLFS): http://mospi.nic.in/
- **Labour Bureau**
  - Annual Survey of Industries (ASI): https://labour.gov.in/
- **National Sample Survey Office (NSSO)**
  - Employment and Unemployment Surveys: http://mospi.nic.in/nsso

## Egypt
- **Central Agency for Public Mobilization and Statistics (CAPMAS)**
  - Labour Force Survey: https://www.capmas.gov.eg/
- **Economic Research Forum (ERF)**
  - Egypt Labor Market Panel Survey (ELMPS): https://erf.org.eg/

## International Organizations
- **International Labour Organization (ILO)**
  - ILOSTAT: https://ilostat.ilo.org/
  - International Standard Classification of Occupations (ISCO): https://www.ilo.org/public/english/bureau/stat/isco/
- **World Bank**
  - World Development Indicators: https://databank.worldbank.org/source/world-development-indicators
  - Jobs Data: https://datacatalog.worldbank.org/search/dataset/0037526

## Data Harmonization Challenges
1. Different occupational classification systems (SOC, ISCO, NOC, etc.)
2. Varying levels of detail in employment and wage data
3. Inconsistent time periods for data collection
4. Different definitions of employment status
5. Varying coverage of informal employment

## Next Steps for Data Collection
1. Download the most recent datasets from each source
2. Create crosswalks between different occupational classification systems
3. Standardize wage data to common currency and time period
4. Extract task-level data from O*NET and similar sources
5. Develop a unified database structure for cross-country analysis
