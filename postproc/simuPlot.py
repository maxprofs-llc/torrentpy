import matplotlib.pyplot as plt
from pandas import DataFrame
import numpy as np
from matplotlib import dates
import logging

from scripts.simuClasses import *
import scripts.simuFiles as sF
import scripts.simuRunSingle as sRS


def main(catchment, outlet):
    # Format given parameters
    catchment = catchment.capitalize()
    outlet = outlet.upper()

    # Location of the different needed directories
    root = os.path.realpath('../..')  # move to parent directory of this current python file
    os.chdir(root)  # define parent directory as root in order to use only relative paths after this
    spec_directory = "scripts/specs/"
    input_directory = "in/"
    output_directory = "out/"

    # Check if combination catchment/outlet is coherent by using the name of the input folder
    if not os.path.exists("{}{}_{}".format(input_directory, catchment, outlet)):
        raise Exception("The combination [ {} - {} ] is incorrect.".format(catchment, outlet))

    # Set up the plotting session (either with .simulation file or through the console)
    data_datetime_start, data_datetime_end, data_time_step_in_min, \
        simu_datetime_start, simu_datetime_end, simu_time_step_in_min, \
        plot_datetime_start, plot_datetime_end = \
        set_up_plotting(catchment, outlet, input_directory)

    # Precise the specific folders to use in the directories
    input_folder = "{}{}_{}/".format(input_directory, catchment, outlet)
    output_folder = "{}{}_{}_{}_{}/".format(output_directory, catchment, outlet,
                                            simu_datetime_start.strftime("%Y%m%d"),
                                            simu_datetime_end.strftime("%Y%m%d"))

    # Create a logger
    logger = sRS.setup_logger(catchment, outlet, 'SinglePlot.main', 'plot', output_folder, is_single_run=True)

    # Create a TimeFrame object
    my__time_frame = TimeFrame(data_datetime_start, data_datetime_end,
                               int(data_time_step_in_min), int(simu_time_step_in_min), 0)

    # Create a Network object from network and waterBodies files
    my__network = Network(catchment, outlet, input_folder, spec_directory)

    # Create a subset of the input discharge file
    sF.get_df_flow_data_from_file(
        catchment, outlet, my__time_frame,
        input_folder, logger).to_csv('{}{}_{}.flow'.format(output_folder,
                                                           catchment.capitalize(),
                                                           outlet),
                                     header='FLOW',
                                     float_format='%e',
                                     index_label='DateTime')

    # Plot the desired graphs
    plot_daily_hydro_hyeto(my__network, my__time_frame,
                           input_folder, output_folder, catchment, outlet,
                           data_datetime_start, data_datetime_end,
                           plot_datetime_start, plot_datetime_end)


def set_up_plotting(catchment, outlet, input_dir):
    try:  # see if there is a .simulation file to set up the simulation
        my_answers_df = pandas.read_csv("{}{}_{}/{}_{}.simulation".format(input_dir, catchment, outlet,
                                                                          catchment, outlet), index_col=0)
    except IOError:
        my_answers_df = DataFrame()

    try:
        question_start_data = my_answers_df.get_value('data_start_datetime', 'ANSWER')
    except KeyError:
        question_start_data = raw_input('Starting date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_data = datetime.datetime.strptime(question_start_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The data starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_data = my_answers_df.get_value('data_end_datetime', 'ANSWER')
    except KeyError:
        question_end_data = raw_input('Ending date for data? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_data = datetime.datetime.strptime(question_end_data, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The data ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_data_time_step = my_answers_df.get_value('data_time_step_min', 'ANSWER')
    except KeyError:
        question_data_time_step = raw_input('Time step for data? [integer in minutes] ')
    try:
        data_time_step_in_min = float(int(question_data_time_step))
    except ValueError:
        raise Exception("The data time step is invalid. [not an integer]")
    try:
        question_start_simu = my_answers_df.get_value('simu_start_datetime', 'ANSWER')
    except KeyError:
        question_start_simu = raw_input('Starting date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_simu = datetime.datetime.strptime(question_start_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The simulation starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_simu = my_answers_df.get_value('simu_end_datetime', 'ANSWER')
    except KeyError:
        question_end_simu = raw_input('Ending date for simulation? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_simu = datetime.datetime.strptime(question_end_simu, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The simulation ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_simu_time_step = my_answers_df.get_value('simu_time_step_min', 'ANSWER')
    except KeyError:
        question_simu_time_step = raw_input('Time step for simulation? [integer in minutes] ')
    try:
        simu_time_step_in_min = float(int(question_simu_time_step))
    except ValueError:
        raise Exception("The simulation time step is invalid. [not an integer]")
    try:
        question_start_plot = my_answers_df.get_value('plot_start_datetime', 'ANSWER')
    except KeyError:
        question_start_plot = raw_input('Starting date for plot? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_start_plot = datetime.datetime.strptime(question_start_plot, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The plot starting date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")
    try:
        question_end_plot = my_answers_df.get_value('plot_end_datetime', 'ANSWER')
    except ValueError:
        question_end_plot = raw_input('Ending date for plot? [format DD/MM/YYYY HH:MM:SS] ')
    try:
        datetime_end_plot = datetime.datetime.strptime(question_end_plot, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        raise Exception("The plot ending date format entered is invalid. [not compliant with DD/MM/YYYY HH:MM:SS]")

    return datetime_start_data, datetime_end_data, data_time_step_in_min, \
        datetime_start_simu, datetime_end_simu, simu_time_step_in_min, \
        datetime_start_plot, datetime_end_plot


def plot_daily_hydro_hyeto(my__network, my__time_frame,
                           in_folder, out_folder, catchment, outlet,
                           dt_start_data, dt_end_data,
                           dt_start_plot, dt_end_plot):

    logger = logging.getLogger('SinglePlot.main')
    logger.info("{} # Reading results files.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

    my_time_dt = my__time_frame.series_data[1:]
    my_time_st = [my_dt.strftime('%Y-%m-%d %H:%M:%S') for my_dt in my_time_dt]

    # Get the average rainfall data over the catchment
    my_rain_mm = np.empty(shape=(len(my_time_st), 0), dtype=np.float64)
    my_area_m2 = np.empty(shape=(0, 1), dtype=np.float64)

    my_dict_desc = sF.get_nd_from_file(my__network, in_folder, extension='descriptors', var_type=float)
    for link in my__network.links:
        try:
            my_df_inputs = pandas.read_csv("{}{}_{}_{}_{}.rain".format(in_folder, catchment, link,
                                                                       dt_start_data.strftime("%Y%m%d"),
                                                                       dt_end_data.strftime("%Y%m%d")),
                                           index_col=0)
        except IOError:
            raise Exception("No rainfall file for {}_{}_{}_{} in {}.".format(
                catchment, link, dt_start_data.strftime("%Y%m%d"), dt_end_data.strftime("%Y%m%d"), in_folder))
        my_rain_mm = np.c_[my_rain_mm, np.asarray(my_df_inputs['RAIN'].loc[my_time_st].tolist())]

        my_area_m2 = np.r_[my_area_m2, np.array([[my_dict_desc[link]['area']]])]
    my_rain_m = my_rain_mm / 1e3  # convert mm to m of rainfall
    catchment_area = np.sum(my_area_m2)  # get the total area of the catchment
    rainfall = my_rain_m.dot(my_area_m2)  # get a list of catchment rainfall in m3
    rainfall *= 1e3/catchment_area  # get rainfall in mm

    # Get the simulated flow at the outlet of the catchment
    simu_flow_m3s = np.empty(shape=(len(my_time_st), 0), dtype=np.float64)
    my_df_node = pandas.read_csv("{}{}_0000.node".format(out_folder, catchment), index_col=0)
    simu_flow_m3s = np.c_[simu_flow_m3s, np.asarray(my_df_node['q_h2o'].loc[my_time_st].tolist())]

    # Get the measured flow near the outlet of the catchment
    gauged_flow_m3s = np.empty(shape=(len(my_time_st), 0), dtype=np.float64)
    gauged_flow_m3s = \
        np.c_[gauged_flow_m3s,
              np.asarray(pandas.read_csv("{}{}_{}.flow".format(out_folder, catchment, outlet),
                                         index_col=0)['flow'].loc[my_time_st].tolist())]

    logger.info("{} # Plotting.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))

    # Plot

    # Create a general figure
    fig = plt.figure(facecolor='white')
    fig.patch.set_facecolor('#ffffff')

    dt_start_data = my_time_dt[0]
    dt_end_data = my_time_dt[-1]

    pyplot_start_data = dates.date2num(dt_start_plot)
    pyplot_end_data = dates.date2num(dt_end_plot)

    if dt_start_data <= dt_start_plot:
        start_diff = dt_start_plot - dt_start_data
        index_start = start_diff.days
    else:
        raise Exception("The start date for plotting is out of bound.")

    if dt_end_plot <= dt_end_data:
        end_diff = dt_end_data - dt_end_plot
        index_end = - (1 + end_diff.days)
    else:
        raise Exception("The end date for plotting is out of bound.")

    # __________________ Hyetograph __________________

    # Create a sub-figure for the hyetograph
    fig1 = fig.add_axes([0.1, 0.7, 0.8, 0.2])  # give location of the graph (%: from left, from bottom, width, height)

    fig1.bar(my_time_dt[index_start:index_end], rainfall[index_start:index_end],
             label='Hyetograph', width=1.0, facecolor='#4ec4f2', edgecolor='#4ec4f2')
    fig1.patch.set_facecolor('none')

    # Get the current axis limits in a tuple (xmin, xmax, ymin, ymax)
    ax1 = plt.axis()
    # Set the limits of the axes (here also invert the y-axis by swapping [2] & [3]
    plt.axis((pyplot_start_data, pyplot_end_data, ax1[3]+1, ax1[2]))

    fig1.spines['left'].set_visible(False)  # Remove axis line
    fig1.spines['bottom'].set_visible(False)
    fig1.get_xaxis().set_ticklabels([])  # Remove X axis values only

    fig1.yaxis.set_ticks_position('right')  # Choose location of axis (value + line): can take left, right, both
    fig1.yaxis.set_label_position('right')
    fig1.set_ylabel('Rainfall (mm)')
    fig1.yaxis.grid(b=True, which='major', linestyle=':')

    for label in fig1.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig1.xaxis.set_ticks_position('top')

    # __________________ Hydrograph __________________

    # Create a sub-figure for the hydrograph
    fig2 = fig.add_axes([0.1, 0.2, 0.8, 0.7])

    # Plot the simulated flows as lines
    fig2.plot(my_time_dt[index_start:index_end], simu_flow_m3s[index_start:index_end], color='#898989',
              label='Modelled')

    # Plot the measured flows as points
    fig2.plot(my_time_dt[index_start:index_end], gauged_flow_m3s[index_start:index_end],
              'x', markersize=2.0, label='Observed', color='#ffc511')

    ax2 = plt.axis()  # Get the current axis limits in a tuple (xmin, xmax, ymin, ymax)
    plt.axis((pyplot_start_data, pyplot_end_data, -0.2, ax2[3]))

    fig2.patch.set_facecolor('none')

    # fig2.fill_between(x, y, y2, color='#f5b171')  # could be use to fill between MIN curve and MAX curve

    fig2.spines['right'].set_visible(True)
    fig2.spines['top'].set_visible(False)
    fig2.yaxis.set_ticks_position('left')
    fig2.xaxis.set_ticks_position('bottom')

    for label in fig2.xaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    for label in fig2.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig2.set_ylabel(u"River Discharge at the outlet (m{}/s)".format(u"\u00B3"))

    fig2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), frameon=False)

    # __________________ Display and Save __________________

    # Show in Tkinter
    # plt.show()

    # Save image
    fig.set_size_inches(11, 6)
    fig.savefig('{}{}_{}.hyeto.hydro.png'.format(out_folder, catchment, outlet),
                dpi=1500, facecolor=fig.get_facecolor(), edgecolor='none')

    logger.info("{} # Ending.".format(datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')))


def plot_flow_duration_curve(obs_flows, obs_frequencies,
                             mod_flows, mod_frequencies,
                             out_folder, catchment, outlet):

    # Create a general figure
    fig = plt.figure(facecolor='white')
    fig.patch.set_facecolor('#ffffff')

    # __________________ FDC Modelled __________________

    # Create a sub-figure for the hydrograph
    fig1 = fig.add_axes([0.1, 0.2, 0.8, 0.7])

    # Plot the simulated flows as lines
    fig1.plot(mod_frequencies, mod_flows, color='#898989', label='Modelled')
    fig1.plot(obs_frequencies, obs_flows, color='#ffc511', label='Observed')

    fig1.patch.set_facecolor('none')

    fig1.yaxis.set_ticks_position('left')
    fig1.xaxis.set_ticks_position('bottom')

    for label in fig1.xaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    for label in fig1.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig1.set_xlabel("Fraction of flow equalled or exceeded (-)")
    fig1.set_ylabel(u"River Discharge (m{}/s)".format(u"\u00B3"))
    fig1.legend(loc='center', bbox_to_anchor=(0.9, 0.9), frameon=False)

    # __________________ Save __________________

    # Save image
    fig.set_size_inches(11, 6)
    fig.savefig('{}{}_{}.fdc.png'.format(out_folder, catchment, outlet),
                dpi=1500, facecolor=fig.get_facecolor(), edgecolor='none')


def plot_flow_duration_curve_log(obs_flows, obs_frequencies,
                                 mod_flows, mod_frequencies,
                                 out_folder, catchment, outlet):

    # Create a general figure
    fig = plt.figure(facecolor='white')
    fig.patch.set_facecolor('#ffffff')

    # __________________ FDC Modelled __________________

    # Create a sub-figure for the hydrograph
    fig1 = fig.add_axes([0.1, 0.2, 0.8, 0.7])

    # Plot the simulated flows as lines
    fig1.semilogy(mod_frequencies, mod_flows, color='#898989', label='Modelled')
    fig1.semilogy(obs_frequencies, obs_flows, color='#ffc511', label='Observed')

    fig1.patch.set_facecolor('none')

    fig1.yaxis.set_ticks_position('left')
    fig1.xaxis.set_ticks_position('bottom')

    for label in fig1.xaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    for label in fig1.yaxis.get_ticklabels():  # If one wants to work on the visual display of the graduation values
        label.set_color('black')
        # label.set_rotation(45)
        label.set_fontsize(10)

    fig1.set_xlabel("Fraction of flow equalled or exceeded (-)")
    fig1.set_ylabel(u"River Discharge (m{}/s)".format(u"\u00B3"))
    fig1.legend(loc='center', bbox_to_anchor=(0.9, 0.9), frameon=False)

    # __________________ Save __________________

    # Save image
    fig.set_size_inches(11, 6)
    fig.savefig('{}{}_{}.fdc.log.png'.format(out_folder, catchment, outlet),
                dpi=1500, facecolor=fig.get_facecolor(), edgecolor='none')

if __name__ == '__main__':
    my_catchment = raw_input('Name of the catchment? ')
    my_outlet = raw_input('European Code (EU_CD) of the catchment? [format IE_XX_##X######] ')
    main(my_catchment, my_outlet)