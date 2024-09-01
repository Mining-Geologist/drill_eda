# DrillEda

DrillEda is a Python package for processing and visualizing drillhole data, particularly in the context of geological and mining exploration.

## Features

- Merge and process geological and assay data.
- Combine lithologies and visualize the data using scatter plots, box plots, and histograms.
- Validate and summarize data.
- Compute descriptive statistics for specific lithologies.

## Installation

```bash 
pip install DrillEda
```


## Example Usage 
```bash 
import pandas as pd
from DrillEda import DrillEda

# Load your data
assay = pd.read_csv('assay.csv')
geology = pd.read_csv('lith.csv')

geology_columns = {
    'holeid': 'ID',
    'from': 'FROM',
    'to': 'TO',
    'rock': 'ROCK'
}

assay_columns = {
    'holeid': 'ID',
    'from': 'FROM',
    'to': 'TO',
    'assay_columns': ['RECOV', 'CU_pct', 'GRADE', 'AG_gpt', 'DENSITY','MO_ppm', 'AS_ppm', 'S_pct']  # Example assay columns
}

# Create an Eda object to store the dataframes
eda = DrillEda()

# Check missing holes in both the geology and assay table, these holes are not included in the combined table
eda.validate_hole_ids(geology, assay, geology_columns, assay_columns)

# Cobmine the Geology and the Assay Table
processed_data = eda.process_data(
    geology, 
    assay, 
    geology_columns, 
    assay_columns, 
    combine_lithologies=True, # if it is set to true it will group the lithologies in the lithology_groups if False it is going to use the orginal geology table 
    lithology_groups={('SAPR','SGNCRLSS'):'SSS'}
)

print(geology)
print(assay)
# Print the combined Geology-Assay Table 
print(processed_data)
# Print the new Geology table with the combined Lithologies
New_geology = eda.get_combined_geology()
print(New_geology)

# Uses a numeric field (grade) and a cutoff values to list the possible Ore lithologies and possible waste lithologies based on the average grade
possible_ore, possible_waste = eda.get_ore_waste_tables('GRADE', 1.0)
# Print the list of the possible ore and possible waste lithologies and their average grades
print(possible_ore)
print(possible_waste)

# Creates a Table with descriptive statistics of a specific lithology in the combined table
descriptive_stats = eda.get_descriptive_statistics('SSS')
print(descriptive_stats)
# Two filters one Categorical and one numerical to be used for the plots

# Categorical Filter using the column Rock to filter only two lithologies
catfilter = {'ROCK': ['E1','E2']}
# Numercial Filter using the column GRADE and and a min and max value 
numfilter = {'GRADE': [0.5, 2.0]}
# Plot a Scatter Plot

eda.scatter('GRADE', # X axis 
            'CU_pct', # y Axis
            dot_size=5,
            dot_color='blue',
            font_size=14,
            catfilter=catfilter,
            numfilter=numfilter,
            num_x_ticks=10, num_y_ticks=10,
            plot_title="Scatter Plot of CU_pct vs GRADE")


# Call the visualize_histogram method
eda.histogram(
    numeric_column='GRADE',
    log_scale=True,        # Set to True if you want the y-axis to be logarithmic
    bin_size=20,            # Number of bins in the histogram
    cap_value=None,         # Optionally cap the values
    bar_color="#3498db",    # Color of the bars
    catfilter=catfilter, 
    numfilter=numfilter     
)


# Call the visualize_boxplot method
eda.boxplot(
    numeric_column='GRADE', # X axis Numerical column
    categorical_column='ROCK', # Y axis Categorical column 
    categories=['SSS', 'E1'],  # Filter specific categories
    box_fill=True,            # Fill the boxes with color
    circle_size=1,            # Size of the outlier circles
    font_size=14,             # Font size for labels and title
    plot_title="Box Plot of GRADE by ROCK",  # Title of the box plot
    log_scale_boxplot=True,# Set to True for log scale on the x-axis
    catfilter=catfilter, 
    numfilter=numfilter 
)
