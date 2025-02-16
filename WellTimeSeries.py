from __future__ import annotations
import yaml 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from PIL import Image

class WellTimeSeries:
    '''
    This class reads the timeseries for a well and creates a 3D diagram
    '''
    def __init__(self, init_folder): 
        '''
        init_folder: the folder that contains the metadata yaml file and the csv file of each reading
        '''
        #loads the metadata file
        self.init_folder = init_folder
        with open(f'{init_folder}/metadata.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file) 
        self.readings = {}
        self.max = 0
        max = 0
        #creates a dictionary containing a dataframe with the CSV file data for each timestamp
        for timestamp, file  in self.config_data["series"].items():
            df = pd.read_csv(f'{init_folder}/{file}', header=0, index_col=0)
            df = self.remove_outliers_corner(df)
            max = df.values.max()
            if max > self.max:
                self.max=max
            self.readings[timestamp]= EmissionExcitationReading(df)
        self.plotted_heatmaps = []

    #this function doesn't run, it is just left in the code in case it is needed in the future
    def remove_outliers_z(self, df):
        flat_values = df.values.flatten()
        # Calculate the overall mean and standard deviation
        mean = np.mean(flat_values)
        std_dev = np.std(flat_values)
        # Calculate Z-scores for all values in the DataFrame
        z_scores = (df - mean) / std_dev
        # Set a threshold for Z-scores (e.g., 3)
        threshold = 3
        # Create a mask for values within the threshold
        mask = np.abs(z_scores) < threshold
        # Apply the mask to keep only values within the threshold
        df_no_outliers = df[mask]
        return df_no_outliers
    
    def remove_outliers_corner(self, df):
        df.iloc[42,0] = 0
        df.iloc[43,0] = 0
        df.iloc[43,1] = 0
        df.iloc[43,2] = 0
        df.iloc[44,0] = 0
        df.iloc[44,1] = 0
        df.iloc[44,2] = 0
        df.iloc[45,0] = 0
        df.iloc[45,1] = 0
        df.iloc[45,2] = 0
        df.iloc[45,3] = 0
        return df


    def plot_heatmaps(self):
        for timestamp, measurment in self.readings.items():
            well_name = self.config_data["well_name"]
            ax=plt.axes()
            sns.heatmap(measurment.get_data(), cmap="icefire", ax=ax, vmax=self.max)
            #sns.heatmap(df, cmap="icefire",  ax=ax, vmax=1000)
            ax.set_title(f'Measurement {timestamp}')
            # Adjust the x and y ticks to make them less dense
            ax.set_xticks(ax.get_xticks()[::5])  
            ax.set_yticks(ax.get_yticks()[::5])  
            heatmap_path = f'{well_name}/file_{timestamp}'
            self.plotted_heatmaps.append(heatmap_path)
            plt.savefig(heatmap_path,dpi=400)
            plt.close()
    
    def export_eem_features(self) -> None:
        for timestamp, measurment in self.readings.items():
            well_name = self.config_data["well_name"]
            features = {"rms" : float(measurment.get_rms()),
                        "peak_shape": float(measurment.get_peak_shape())}
            with open(f'{well_name}_eem_features.yml', 'w') as f:
                yaml.safe_dump(features, f)


    def make_gif(self):
        # Load images
        images = [Image.open(f'{img}.png') for img in self.plotted_heatmaps]
        gif_path = self.init_folder +'timeseries.gif'
        images[0].save(
            gif_path,
            save_all=True,
            append_images=images[1:],
            duration=400,  # Duration between frames in milliseconds
            loop=0  # Loop forever
            )

class EmissionExcitationReading:
    def __init__(self, df: pd.DataFrame) -> None:
        self._data: pd.DataFrame = df
        self._data_normalised: pd.DataFrame = df/df.max()
        self._peak_limit_normalised = 0.8 
    
    def get_data(self) -> pd.DataFrame:
        return self._data
    
    def get_data_normalised(self) -> pd.DataFrame:
        return self._data_normalised
    
    def get_rms(self) -> float:
        data = self._data_normalised.to_numpy()
        return np.sqrt(np.mean(data**2))
    
    def get_peak_shape(self, peak_a_emission_min = 510, peak_a_emission_max = 554, 
                       peak_b_emission_min = 556, peak_b_emission_max = 650,
                       peak_b_excitation_min = None, peak_b_excitation_max = None,
                       peak_a_excitation_min = None, peak_a_excitation_max = None,) ->float:

        peak_a = pd.DataFrame()
        peak_b = pd.DataFrame()
        columns = self._data_normalised.columns
        for column in columns:
            if peak_a_emission_min <= float(column) < peak_a_emission_max:
                peak_a[column] = self._data_normalised[column]
            elif peak_b_emission_min <= float(column) < peak_b_emission_max:
                peak_b[column] = self._data_normalised[column]
        return peak_b.to_numpy().sum()/peak_a.to_numpy().sum()
    
    def get_euclidean_distance(self, emmision_excitation_reading: EmissionExcitationReading) -> float:
        return np.sum(np.square(self._data_normalised.to_numpy() - emmision_excitation_reading.get_data_normalised().to_numpy()))
        

if __name__ == "__main__":
    with open('well_names.yaml', 'r') as file:
        total_wells = yaml.safe_load(file)
    for well in total_wells:        
        well = WellTimeSeries(f'./{well}')
        # well.plot_heatmaps()
        well.make_gif()