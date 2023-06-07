import React, { useEffect, useState, useRef } from "react";
import {
  VictoryChart,
  VictoryLabel,
  VictoryAxis,
  VictoryContainer,
  VictoryLegend,
  VictoryTheme,
  VictoryLine,
  VictoryScatter,
  VictoryTooltip,
} from "victory";

import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { FiCalendar } from 'react-icons/fi';
import Popover from '@material-ui/core/Popover';
import DateRangeIcon from '@material-ui/icons/DateRange';
import { IconButton, ButtonGroup, Button } from '@material-ui/core';
import '../css/latency.css'

import { getLatency } from "./DataAccessLayer";

function LatencyChart() {
  const [latencyState, setLatencyState] = useState([]);
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [isOpen, setIsOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const buttonRef = useRef(null);
  const [activeButton, setActiveButton] = useState('');
  

  // const [filteredData, setFilteredData] = useState();
  const CustomInput = React.forwardRef(({ value, onClick }, ref) => (
    <button className="bg-gray-600 p-2 rounded text-white ml-4" onClick={onClick} ref={ref}>
      <FiCalendar/> {value}
    </button>
  ));
  

  useEffect(() => {
    getLatencyData();
  }, [startDate, endDate]);

  const getLatencyData = async () => {
    const data = await getLatency();
    console.log("anime1")
    console.log(data.data.end_date)
    console.log(data.data.map(d => {
      var dateString = d.end_date;
      var parts = dateString.split("-");
      var formattedDateString = "20" + parts[2] + "-" + parts[1] + "-" + parts[0];
      const date = new Date(formattedDateString);
      return date;
    }))
    // Фильтруем данные на основе выбранных дат
    const filteredData = data.data.filter(d => {
      var dateString = d.end_date;
      var parts = dateString.split("-");
      var formattedDateString = "20" + parts[2] + "-" + parts[1] + "-" + parts[0];
      const date = new Date(formattedDateString);
      return date >= new Date(startDate) && date <= new Date(endDate);
    });

    setLatencyState(filteredData);
    console.log("anime")
    console.log(filteredData)
    console.log(startDate)
    console.log(endDate)
  };

  const generateTickValues = () => {
    if (latencyState.length > 7) {
      return [];
    } else {
      return latencyState.map(data => data.range_date);
    }
  };
  const [tickValues, setTickValues] = useState(generateTickValues());
  useEffect(() => {
    setTickValues(generateTickValues());
  }, [latencyState]);

  const onDatesChange = (dates) => {
    const [start, end] = dates;
    setStartDate(start);
    setEndDate(end);
  };

  const isMonday = date => {
    const day = date.getDay();
    return day === 1;
  };

  const isSunday = date => {
    const day = date.getDay();
    return day === 0;
  };

  const setLastMonth = () => {
    const now = new Date();
    const oneMonthAgo = new Date(now.setMonth(now.getMonth() - 1));
    setStartDate(oneMonthAgo);
    setEndDate(new Date());
    setActiveButton('1m');
  };

  const setLastHalfYear = () => {
    const now = new Date();
    const sixMonthsAgo = new Date(now.setMonth(now.getMonth() - 6));
    setStartDate(sixMonthsAgo);
    setEndDate(new Date());
    setActiveButton('6m');
  };

  const setLastYear = () => {
    const now = new Date();
    const oneYearAgo = new Date(now.setFullYear(now.getFullYear() - 1));
    setStartDate(oneYearAgo);
    setEndDate(new Date());
    setActiveButton('1y');
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
    setActiveButton('custom');
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? 'simple-popover' : undefined;
  

  return (
    <div>
      <div class="h3 text-center">
        <h3>Average Censorship Latency</h3>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0 justify-center mx-8">
      <div className="mb-4">
        <label className="block text-sm mb-2">Select Date Range:</label>
        {/* <IconButton aria-describedby={id} variant="contained" color="primary" onClick={handleClick}>
          <DateRangeIcon />
        </IconButton> */}
        <Popover
          id={id}
          open={open}
          anchorEl={anchorEl}
          onClose={handleClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'center',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'center',
          }}
        >
          <DatePicker
            selected={startDate}
            onChange={onDatesChange}
            startDate={startDate}
            endDate={endDate}
            shouldUnregister={true}
            selectsRange
            inline
            calendarStartDay={1}
            portalId="root-portal"
            filterDate={date => (startDate && !endDate ? isSunday(date) : isMonday(date))}
            className="bg-gray-600 p-2 rounded text-white"
          />
        </Popover>
        <div className="mb-4">
        <label className="block text-sm mb-2">Select Date Range:</label>
        <ButtonGroup variant="contained" color="primary" aria-label="contained primary button group">
          <Button
            variant={activeButton === 'custom' ? "contained" : "outlined"}
            color="primary"
            onClick={handleClick}
            startIcon={<DateRangeIcon />}
          >
          </Button>
          <Button
            variant={activeButton === '1m' ? "contained" : "outlined"}
            onClick={setLastMonth}
          >
            1m
          </Button>
          <Button
            variant={activeButton === '6m' ? "contained" : "outlined"}
            onClick={setLastHalfYear}
          >
            6m
          </Button>
          <Button
            variant={activeButton === '1y' ? "contained" : "outlined"}
            onClick={setLastYear}
          >
            1y
          </Button>
        </ButtonGroup>
      </div>
      </div>
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] laptop:w-[700px]  laptop:h-[700px]">
          <VictoryChart
            height={600}
            width={600}
            padding={{ bottom: 130, left: 100, right: 100, top: 50 }}
            minDomain={{ y: 0 }}
            maxDomain={{ y: 25 }}
            theme={VictoryTheme.material}
            containerComponent={
              <VictoryContainer
                style={{
                  // pointerEvents: "auto",
                  userSelect: "auto",
                  touchAction: "auto",
                }}
              />
            }
          >
            <VictoryLegend
              x={50}
              y={0}
              orientation="horizontal"
              gutter={15}
              style={{ labels: { fontSize: 15 } }}
              data={[
                {
                  name: "Average Сensorship Latency",
                  symbol: { fill: "#1e90ff" },
                  labels: { fill: "#FFFFFF" },
                },
                {
                  name: "Average Censorship Latency if Lido was\n completely non-censoring",
                  symbol: { fill: "#c43a31" },
                  labels: { fill: "#FFFFFF" },
                },
              ]}
            />
            <VictoryLine
              alignment="middle"
              style={{ data: { stroke: "#c43a31" } }}
              data={latencyState}
              x="range_date"
              y="overall_censorship_latency_without_lido_censorship"
            />
            <VictoryLine
              alignment="middle"
              style={{ data: { stroke: "#1e90ff" } }}
              // labels={({ datum }) => datum.y}
              data={latencyState}
              x="range_date"
              y="overall_censorship_latency"
            />
            <VictoryScatter
              data={latencyState}
              x="range_date"
              y="overall_censorship_latency"
              size={7}
              style={{
                data: { fill: "white" },
                labels: { fill: "white" },
              }}
              labels={({ datum }) =>
                `latency: ${datum.overall_censorship_latency.toFixed(4)}`
              }
              labelComponent={
                <VictoryTooltip
                  dy={0}
                  style={{ fill: "black" }}
                  flyoutWidth={150}
                />
              }
            />
            <VictoryScatter
              data={latencyState}
              x="range_date"
              y="overall_censorship_latency_without_lido_censorship"
              size={7}
              style={{
                data: { fill: "white" },
                labels: { fill: "white" },
              }}
              labels={({ datum }) =>
                `latency: ${datum.overall_censorship_latency_without_lido_censorship.toFixed(
                  4
                )}`
              }
              labelComponent={
                <VictoryTooltip
                  dy={0}
                  style={{ fill: "black" }}
                  flyoutWidth={150}
                />
              }
            />
            <VictoryAxis
              dependentAxis
              // tickFormat={(t) => `${t}%`}
              style={{ tickLabels: { fontSize: 19, fill: "#FFFFFF" } }}
              
              label="LATENCY"
              tickFormat={(t) => `${t}s`}
              axisLabelComponent={
                <VictoryLabel
                  style={[{ fill: "#FFFFFF", fontSize: 30 }]}
                  dy={-60}
                  padding={100}
                />
              }
            />
            <VictoryAxis
              style={{ tickLabels: { fontSize: 10, fill: "#FFFFFF" } }}
              tickValues={tickValues}
              label="DATE"
              axisLabelComponent={
                <VictoryLabel
                  dy={70}
                  style={[{ fill: "#FFFFFF", fontSize: 30 }]}
                />
              }
            />
          </VictoryChart>
        </div>
        <div class="desktop:w-[500px] laptop:max-w-[500px] laptop:min-w-[300px] ">
          <p class="desktop:text-xl uwdesktop:text-2xl">
            <b> Censorship Latency</b>
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            The Censorship Latency metric measures the difference in average
            waiting time for transactions with similar features, except for
            their OFAC compliance status. We use a binary classifier with high
            accuracy to predict the number of blocks for which non-OFAC
            compliant transactions were not included due to censorship. This
            number is then multiplied by 12 to calculate the Censorship Latency
            metric.
          </p>
          <br></br>
          <p class="desktop:text-xl uwdesktop:text-2xl">
            <b>
            Average Censorship Latency if Lido was completely non-censoring 
            </b>
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            We also
            compute a modified version of the Censorship Latency metric by
            assuming that the Lido validators were completely non-censoring.
            This adjusted metric helps to understand the impact of censorship by
            other validators on the overall network.
          </p>
          <br></br>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            Example of metric calculation:
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            A transaction was twice censored by other validators and then once
            by Lido before being included in a block by another validator:
          </p>
          <br></br>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            Block #1 - Censored by Non Lido validator
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            Block #2 - Censored by Non Lido validator
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            Block #3 - Censored by Lido validator
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            Block #4 - Included in a block by Non Lido validator
          </p>
          <br></br>
          <p>For this case:</p>
          <ul class="list-disc list-inside">
            <li>
              Censorship Latency will be calculated as 3 blocks (Block #1, #2,
              and #3) multiplied by 12 seconds = 36 seconds.
            </li>
            <li>
              Lido-adjusted Censorship Latency will be calculated as 2 blocks
              (Block #1 and #2) multiplied by 12 seconds = 24 seconds. Here, we
              expect the Lido validator to include the transaction in Block #3.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default LatencyChart;
