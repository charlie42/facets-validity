# lisa-school-2024

1. Create `input` directory, copy:
- .json FACETS file named `facets.json`
- .csv file with SDQ scores named `sdq.csv`
- .csv file with diagnostics names `diagnostics.csv`, rename `anonimised id` to `Study ID`
- .csv file with mapping between FACETS ID and Study ID named `id_mapping_facets.csv`
2. Run `data_preprocessing.py` to transform the json FACETS file into .csv file
4. Run script in `paper_analysis` folder to create reports

`data_exploration.py` includes additional analysis