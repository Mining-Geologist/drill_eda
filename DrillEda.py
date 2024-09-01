import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random

class DrillEda:
    def __init__(self):
        self.combined_geology = None
        self.filtered_data = None

    def merge_data(self, row, geology, assay, geology_columns, assay_columns):
        geology_data = geology[(geology[geology_columns['holeid']] == row['ID']) &
                               (geology[geology_columns['from']] <= row['FROM']) &
                               (geology[geology_columns['to']] > row['FROM'])]

        assay_data = assay[(assay[assay_columns['holeid']] == row['ID']) &
                           (assay[assay_columns['from']] <= row['FROM']) &
                           (assay[assay_columns['to']] > row['FROM'])]

        geology_result = geology_data[geology_columns['rock']].iloc[0] if not geology_data.empty else None
        assay_result = assay_data[assay_columns['assay_columns']].iloc[0] if not assay_data.empty else pd.Series([None]*len(assay_columns['assay_columns']), index=assay_columns['assay_columns'])

        return pd.concat([pd.Series({'ROCK': geology_result}), assay_result])

    def merge_consecutive_intervals(self, df, geology_columns):
        merged_intervals = []
        current_interval = df.iloc[0].copy()

        for i in range(1, len(df)):
            if (df.iloc[i][geology_columns['rock']] == current_interval[geology_columns['rock']]) and (df.iloc[i]['ID'] == current_interval['ID']):
                # Extend the current interval
                current_interval[geology_columns['to']] = df.iloc[i][geology_columns['to']]
            else:
                # Save the current interval and start a new one
                merged_intervals.append(current_interval.copy())
                current_interval = df.iloc[i].copy()

        # Append the last interval
        merged_intervals.append(current_interval)

        return pd.DataFrame(merged_intervals)

    def process_data(self, geology, assay, geology_columns, assay_columns, combine_lithologies=False, lithology_groups=None):
        # Check unique hole IDs in both tables
        geology_hole_ids = set(geology[geology_columns['holeid']].unique())
        assay_hole_ids = set(assay[assay_columns['holeid']].unique())

        common_hole_ids = geology_hole_ids.intersection(assay_hole_ids)
        # Filter out IDs that are not in both tables
        geology = geology[geology[geology_columns['holeid']].isin(common_hole_ids)]
        assay = assay[assay[assay_columns['holeid']].isin(common_hole_ids)]

        # Optionally combine lithologies
        if combine_lithologies and lithology_groups:
            for lithologies, new_name in lithology_groups.items():
                for lith in lithologies:
                    geology.loc[geology[geology_columns['rock']] == lith, geology_columns['rock']] = new_name

            geology = geology.sort_values([geology_columns['holeid'], geology_columns['from']])
            geology = self.merge_consecutive_intervals(geology, geology_columns)

        self.combined_geology = geology

        # Combine unique depths for each drillhole
        # Ensure proper alignment of columns before concatenation
        geology_from_aligned = self.combined_geology[[geology_columns['holeid'], geology_columns['from']]].rename(columns={geology_columns['holeid']: 'ID', geology_columns['from']: 'FROM'})
        geology_to_aligned = self.combined_geology[[geology_columns['holeid'], geology_columns['to']]].rename(columns={geology_columns['holeid']: 'ID', geology_columns['to']: 'FROM'})
        assay_from_aligned = assay[[assay_columns['holeid'], assay_columns['from']]].rename(columns={assay_columns['holeid']: 'ID', assay_columns['from']: 'FROM'})
        assay_to_aligned = assay[[assay_columns['holeid'], assay_columns['to']]].rename(columns={assay_columns['holeid']: 'ID', assay_columns['to']: 'FROM'})

        combined_depths = (pd.concat([
            geology_from_aligned,
            geology_to_aligned,
            assay_from_aligned,
            assay_to_aligned
        ])
        .drop_duplicates()
        .sort_values(['ID', 'FROM']))


        # Create intervals
        combined_depths['TO'] = combined_depths.groupby('ID')['FROM'].shift(-1)
        combined_depths = combined_depths.dropna()

        # Merge data for each interval
        merged_data = combined_depths.apply(self.merge_data, axis=1, geology=self.combined_geology, assay=assay, geology_columns=geology_columns, assay_columns=assay_columns)

        # Combine merged data with the interval data
        self.filtered_data = pd.concat([combined_depths.reset_index(drop=True), merged_data.reset_index(drop=True)], axis=1)

        return self.filtered_data

    def get_combined_geology(self):
        return self.combined_geology
    



    def get_ore_waste_tables(self, grade_column, cutoff):
        if self.filtered_data is None:
            raise ValueError("No data available. Please run the process_data method first.")

        lithology_means = self.filtered_data.groupby('ROCK')[grade_column].mean().dropna()

        # Possible ore lithologies (above the cutoff)
        possible_ore = lithology_means[lithology_means >= cutoff]

        # Possible waste lithologies (below the cutoff)
        possible_waste = lithology_means[lithology_means < cutoff]

        return possible_ore, possible_waste
    




    def apply_filters(self, catfilter=None, numfilter=None):
        data = self.filtered_data.copy()

        if catfilter:
            for col, values in catfilter.items():
                data = data[data[col].isin(values)]
        
        if numfilter:
            for col, (min_val, max_val) in numfilter.items():
                data = data[(data[col] >= min_val) & (data[col] <= max_val)]
        
        return data



    def scatter(self, x_axis, y_axis, catfilter=None, numfilter=None, dot_size=5, dot_color='#FF6347', font_size=12, num_x_ticks=10, num_y_ticks=10, x_label_rotation=0, plot_title=None):
        filtered_data = self.apply_filters(catfilter, numfilter)
        if not filtered_data.empty:
            fig, ax = plt.subplots()
            ax.scatter(filtered_data[x_axis], filtered_data[y_axis], s=dot_size, c=dot_color, alpha=0.7)
            ax.set_xlabel(x_axis, fontsize=font_size)
            ax.set_ylabel(y_axis, fontsize=font_size)
            ax.set_title(plot_title if plot_title else f"{y_axis} vs {x_axis}", fontsize=16)

            ax.xaxis.set_major_locator(plt.MaxNLocator(num_x_ticks))
            ax.yaxis.set_major_locator(plt.MaxNLocator(num_y_ticks))
            ax.tick_params(axis='x', labelsize=font_size, rotation=x_label_rotation)
            ax.tick_params(axis='y', labelsize=font_size)

            plt.show()

    def boxplot(self, numeric_column, categorical_column, categories=None, catfilter=None, numfilter=None, box_fill=True, circle_size=5, font_size=12, plot_title=None, log_scale_boxplot=False):
        filtered_data = self.apply_filters(catfilter, numfilter)
        if categories:
            filtered_data = filtered_data[filtered_data[categorical_column].isin(categories)]

        if not filtered_data.empty:
            fig, ax = plt.subplots()
            if log_scale_boxplot:
                ax.set_xscale('log')

            filtered_data.boxplot(column=numeric_column, by=categorical_column, ax=ax, vert=False, patch_artist=box_fill, flierprops=dict(marker='o', markersize=circle_size))

            if box_fill:
                box_colors = [f"#{random.randint(0, 0xFFFFFF):06x}" for _ in categories]
                for patch, color in zip(ax.artists, box_colors):
                    patch.set_facecolor(color)

            ax.set_title(plot_title if plot_title else f"{numeric_column} by {categorical_column}", fontsize=font_size)
            ax.set_ylabel(categorical_column, fontsize=font_size)
            ax.set_xlabel(numeric_column, fontsize=font_size)
            ax.tick_params(axis='both', labelsize=font_size)

            plt.suptitle("")  # Remove the default boxplot title
            plt.show()

    def histogram(self, numeric_column, catfilter=None, numfilter=None, log_scale=False, bin_size=20, cap_value=None, bar_color="#3498db"):
        filtered_data = self.apply_filters(catfilter, numfilter)
        if not filtered_data.empty:
            data = filtered_data[numeric_column]
            if cap_value is not None:
                data = data.apply(lambda x: min(x, cap_value))

            fig, ax = plt.subplots()
            ax.hist(data, bins=bin_size, log=log_scale, edgecolor='black', color=bar_color)
            ax.set_xlabel(numeric_column)
            ax.set_ylabel("Frequency")
            ax.set_title(f"Histogram of {numeric_column}")

            plt.show()

    def validate_hole_ids(self,geology, assay, geology_columns, assay_columns):
        # Get unique Hole IDs from both geology and assay tables
        geology_hole_ids = set(geology[geology_columns['holeid']].unique())
        assay_hole_ids = set(assay[assay_columns['holeid']].unique())

        # Compare the sets to find missing Hole IDs
        missing_in_assay = geology_hole_ids - assay_hole_ids
        missing_in_geology = assay_hole_ids - geology_hole_ids

        # Print the results
        if missing_in_assay:
            print(f"Hole IDs missing in Assay Table ({len(missing_in_assay)}): {list(missing_in_assay)}")
        else:
            print("No Hole IDs are missing in the Assay Table.")

        if missing_in_geology:
            print(f"Hole IDs missing in Geology Table ({len(missing_in_geology)}): {list(missing_in_geology)}")
        else:
            print("No Hole IDs are missing in the Geology Table.")
    
    def get_descriptive_statistics(self, lith):
        if self.filtered_data is None:
            raise ValueError("No data available. Please run the process_data method first.")

        # Filter the data for the specified lithologies
        filtered_data = self.filtered_data[self.filtered_data['ROCK']==lith]

        # Calculate descriptive statistics for all numeric fields
        descriptive_stats = filtered_data.describe()

        return descriptive_stats