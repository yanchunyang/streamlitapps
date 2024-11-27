import streamlit
import pandas
import scipy.stats as stats
from statsmodels.stats.power import tt_ind_solve_power

def upload_file():
    uploaded_file = streamlit.file_uploader("Choose a file")
    if uploaded_file is not None:
        dataframe = pandas.read_csv(uploaded_file)
        return dataframe
    return None

data = upload_file()
if data is not None:
    streamlit.write("data has been uploaded")

    if data is not None:
        num_rows = data.shape[0]
        column_names = data.columns.tolist()

        streamlit.write(f"The dataset has {num_rows} rows.")
        streamlit.write("---")  # Draw a line to separate sections

        # Display dataset basic characteristics
        num_columns = data.shape[1]
        column_info = data.dtypes
        null_values = data.isnull().sum()

        streamlit.write(f"The dataset has {num_columns} columns.")
        streamlit.write("Column information:")
        for col in column_names:
            streamlit.write(f"- {col}: {column_info[col]}, Null values: {null_values[col]}")
        # Calculate and display mean value of each numeric column
        numeric_columns = data.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            mean_value = data[col].mean()
            streamlit.write(f"Mean value of {col}: {mean_value}")

         # Display unique values for each non-numeric column
        non_numeric_columns = data.select_dtypes(exclude=['number']).columns
        for col in non_numeric_columns:
            unique_values = data[col].nunique()
            streamlit.write(f"Number of unique values in {col}: {unique_values}")

        # Add a multiple choice widget to select columns for histogram
        selected_columns = streamlit.multiselect("Select columns to draw histograms", numeric_columns)

        # Draw histogram for each selected column
        for col in selected_columns:
            streamlit.write(f"Histogram for {col}:")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.hist(data[col], bins=30)
            streamlit.pyplot(fig)


        streamlit.write("---")  # Draw a line to separate sections
        selected_column = streamlit.selectbox("Select a column to analyze", column_names)
        group_column = streamlit.selectbox("Select a column to group by", column_names)

        if selected_column and group_column:
             # Create a table with group column as rows and mean values of all numeric columns as columns
            grouped_means = data.groupby(group_column)[numeric_columns].mean()
            streamlit.write(f"Mean values of numeric columns grouped by {group_column}:")
            streamlit.dataframe(grouped_means)

        if selected_column and group_column:
            groups = data[group_column].unique()
            group_data = [data[data[group_column] == group][selected_column] for group in groups]

            b_value = streamlit.number_input("Input the b value", value=0.0)
            a_value = streamlit.number_input("Input the a value", value=0.0)
            mean_values = data.groupby(group_column)[selected_column].mean()
            streamlit.write(f"Mean values of {selected_column} by {group_column}:")
            streamlit.write(mean_values)
            minimal_detectable_value = streamlit.number_input("Input the minimal detectable value", value=0.0)
            # Calculate the minimal sample size for the given power and effect size
            if minimal_detectable_value:
                effect_size = minimal_detectable_value / data[selected_column].std()

                sample_size = tt_ind_solve_power(effect_size=effect_size, alpha=a_value, power=b_value, ratio=1.0, alternative='two-sided')

                streamlit.write(f"Minimal sample size required for the given power and effect size: {sample_size}")

            if b_value and a_value:

                if len(groups) == 2:
                    t_stat, p_value = stats.ttest_ind(group_data[0], group_data[1])
                    streamlit.write(f"T-test result: t-statistic = {t_stat}, p-value = {p_value}")
                else:
                    f_stat, p_value = stats.f_oneway(*group_data)
                    streamlit.write(f"ANOVA result: F-statistic = {f_stat}, p-value = {p_value}")

                if p_value < 0.05:
                    streamlit.write("The difference in means is statistically significant.")
                else:
                    streamlit.write("The difference in means is not statistically significant.")
