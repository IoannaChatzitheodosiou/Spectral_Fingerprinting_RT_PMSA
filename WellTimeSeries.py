from __future__ import annotations
import yaml 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from PIL import Image

class WellTimeSeriesPlotter:
    def __init__(self, well_time_series: WellTimeSeries) -> None:
        self.readings = well_time_series.readings
        self._euclidean_distances_over_timeseries = well_time_series._euclidean_distances_over_timeseries
        self._eem_features = well_time_series._eem_features
        self.config_data =  well_time_series.config_data
        self.plotted_heatmaps = []
        self.max = well_time_series.max
        self.init_folder = well_time_series.init_folder

    def plot_reading_heatmap(self) -> None:
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

    def plot_euclidean_heatmap(self) -> None:
        sns.heatmap(self._euclidean_distances_over_timeseries, cmap="icefire")
        plt.savefig('euclidean_distance_over_time',dpi=400)
        plt.close()

    def plot_eem_features(self)-> None:
        plt.figure(figsize=(8, 5))
        plt.scatter(self._eem_features['rms'], self._eem_features['peak_shape'], color='blue')
        for index in self._eem_features.index:
            plt.text(self._eem_features['rms'][index], self._eem_features['peak_shape'][index], 
                     index, fontsize=12, ha='right', va='bottom')
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.title("Scatter Plot with Index Labels")
        plt.savefig('eem_features_over_time',dpi=400)
        plt.close()

    def make_gif(self) -> None:
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

class WellTimeSeries:
    '''
    This class reads the timeseries for a well and creates a 3D diagram
    '''
    def __init__(self, init_folder: str, remove_outliars: function) -> None: 
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
            df = remove_outliars(df)
            max = df.values.max()
            if max > self.max:
                self.max=max
            self.readings[timestamp]= EmissionExcitationReading(df)
        self.plotted_heatmaps = []
        self._euclidean_distances_over_timeseries: pd.DataFrame = self.euclidean_distance_between_timepoints()
        self._eem_features: pd.DataFrame = self.calculate_eem_features()
    
    def calculate_eem_features(self) -> pd.DataFrame:
        features_table = pd.DataFrame()
        for timestamp, measurment in self.readings.items():
            well_name = self.config_data["well_name"]
            features = {"rms" : float(measurment.get_rms()),
                        "peak_shape": float(measurment.get_peak_shape())}
            features_table = pd.concat([features_table, pd.DataFrame([features], index=[timestamp])])
            with open(f'{well_name}_eem_features.yml', 'w') as f:
                yaml.safe_dump(features, f)
        return features_table

    def euclidean_distance_between_timepoints(self) -> pd.DataFrame:
        distances_table = pd.DataFrame()
        for timestamp, read in self.readings.items():
            euclidean_distance = {}
            for timestamp2, read2 in self.readings.items():
                euclidean_distance[timestamp2] = read.get_euclidean_distance(read2)
            distances_table = pd.concat([distances_table, pd.DataFrame([euclidean_distance], index=[timestamp])])
        return distances_table

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