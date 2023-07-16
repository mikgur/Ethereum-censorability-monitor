import React, { useEffect, useState, useRef } from "react";
import {
  VictoryChart,
  VictoryLabel,
  VictoryAxis,
  VictoryLegend,
  VictoryLine,
  VictoryScatter,
  VictoryTooltip,
  createContainer, 
  VictoryVoronoiContainer,
} from "victory";

import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { FiCalendar } from 'react-icons/fi';
import Popover from '@material-ui/core/Popover';
import DateRangeIcon from '@material-ui/icons/DateRange';
import { IconButton, ButtonGroup, Button } from '@material-ui/core';
import '../css/latency.css'
import { startOfWeek, endOfWeek } from "date-fns";

import { getLatency } from "./DataAccessLayer";

function LatencyChart() {
  const getMonday = (date) => startOfWeek(date, { weekStartsOn: 1 });
  const getSunday = (date) => endOfWeek(date, { weekStartsOn: 1 });

  const [latencyState, setLatencyState] = useState([]);
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(getSunday(new Date()));
  const [isOpen, setIsOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const buttonRef = useRef(null);
  const [activeButton, setActiveButton] = useState('');

  useEffect(() => {
    getLatencyData();
  }, [startDate, endDate]);

  useEffect(() => {
    setLastHalfYear();
  }, []);

  

  const getLatencyData = async () => {
    const data = await getLatency();
    // Фильтруем данные на основе выбранных дат
    const filteredData = data.data.filter(d => {
      var dateString = d.end_date;
      var parts = dateString.split("-");
      var formattedDateString = "20" + parts[2] + "-" + parts[1] + "-" + parts[0];
      const date = new Date(formattedDateString);
      const endDatePlusOneWeek = new Date(endDate.getTime());
      endDatePlusOneWeek.setDate(endDatePlusOneWeek.getDate() + 7);
      return date >= new Date(startDate) && date < endDatePlusOneWeek;
    });
  
    setLatencyState(filteredData);
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
    setEndDate(new Date())
    setActiveButton('1m');
  };

  const setLastHalfYear = () => {
    const now = new Date();
    const sixMonthsAgo = new Date(now.setMonth(now.getMonth() - 6));
    setStartDate(sixMonthsAgo);
    setEndDate(new Date())
    setActiveButton('6m');
  };

  const setLastYear = () => {
    const now = new Date();
    const oneYearAgo = new Date(now.setFullYear(now.getFullYear() - 1));
    setStartDate(oneYearAgo);
    setEndDate(new Date())
    setActiveButton('1y');
  };

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
    setActiveButton('custom');
  };

  const handleClose = () => {
    setAnchorEl(null);
  };
  let prevMonth = null;

  const getDateOnStr = (strDate) => {
    var parts = strDate.split("\n — \n");
    var partsOneDate = parts[0].split('-')
    var formattedDateString = "20" + partsOneDate[2] + "-" + partsOneDate[1] + "-" + partsOneDate[0];
    const date = new Date(formattedDateString);
    return date;
  }
  const getTooltipLabel = (datum) =>
  `${datum.range_date.replace(/[\n]/g, '')}\n \n ${datum.overall_censorship_latency.toFixed(4)}\n ${datum.overall_censorship_latency_without_lido_censorship.toFixed(4)}`;

// Создайте два массива точек: один для каждого из ваших наборов данных
const points1 = latencyState.map(item => ({
  x: item.range_date,
  y: item.overall_censorship_latency,
  label: getTooltipLabel(item),
}));

const points2 = latencyState.map(item => ({
  x: item.range_date,
  y: item.overall_censorship_latency_without_lido_censorship,
}));

  const open = Boolean(anchorEl);
  const id = open ? 'simple-popover' : undefined;
  

  return (
    <div>
      <div class="h3 text-center">
        <h3>Average Censorship Latency</h3>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0 justify-center mx-8">
        <div class="flex flex-col items-center mx-8">
          <div className="mb-4 mx-8 justify-center">
            <Popover
              id={id}
              open={open}
              anchorEl={anchorEl}
              onClose={handleClose}
              anchorOrigin={{
                vertical: "bottom",
                horizontal: "center",
              }}
              transformOrigin={{
                vertical: "top",
                horizontal: "center",
              }}
            >
              <DatePicker
                selected={startDate}
                onChange={onDatesChange}
                // startDate={getMonday(startDate)}
                startDate={getMonday(startDate)}
                endDate={endDate}
                shouldUnregister={true}
                selectsRange
                inline
                calendarStartDay={1}
                portalId="root-portal"
                filterDate={(date) =>
                  startDate && !endDate
                    ? isSunday(date) &&
                      date.getTime() >=
                        startOfWeek(startDate, { weekStartsOn: 1 }).getTime()
                    : isMonday(date)
                }
                className="bg-white p-2 rounded text-black"
              />
            </Popover>
            <div className="mb-4">
              <ButtonGroup
              // variant="contained"
              // aria-label="contained button group"
              >
                <Button
                  variant={activeButton === "custom" ? "contained" : "outlined"}
                  onClick={handleClick}
                  startIcon={<DateRangeIcon />}
                  style={{
                    transition: "background 0.3s ease",
                    background:
                      activeButton === "custom" ? "#319795" : "#6b7280",
                    margin: "0px",
                    color: activeButton === "custom" ? "white" : "#d1d5db",
                  }}
                ></Button>
                <Button
                  variant={activeButton === "1m" ? "contained" : "outlined"}
                  onClick={setLastMonth}
                  style={{
                    transition: "background 0.3s ease",
                    background: activeButton === "1m" ? "#319795" : "#6b7280",
                    margin: "0px",
                    color: activeButton === "1m" ? "white" : "#d1d5db",
                  }}
                >
                  1m
                </Button>
                <Button
                  variant={activeButton === "6m" ? "contained" : "outlined"}
                  onClick={setLastHalfYear}
                  style={{
                    transition: "background 0.3s ease",
                    background: activeButton === "6m" ? "#319795" : "#6b7280",
                    margin: "0px",
                    color: activeButton === "6m" ? "white" : "#d1d5db",
                  }}
                >
                  6m
                </Button>
                <Button
                  variant={activeButton === "1y" ? "contained" : "outlined"}
                  onClick={setLastYear}
                  style={{
                    transition: "background 0.3s ease",
                    background: activeButton === "1y" ? "#319795" : "#6b7280",
                    margin: "0px",
                    color: activeButton === "1y" ? "white" : "#d1d5db",
                  }}
                >
                  1y
                </Button>
              </ButtonGroup>
            </div>
          </div>
          <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] laptop:w-[600px]  laptop:h-[700px]">
            <VictoryChart
              height={600}
              width={600}
              padding={{ bottom: 130, left: 100, right: 100, top: 50 }}
              minDomain={{ y: 0 }}
              maxDomain={{ y: 25 }}
              containerComponent={
                <VictoryVoronoiContainer voronoiDimension="x" />
              }
            >
              <VictoryScatter
                data={points1}
                size={({ active }) => (active ? 3 : 1)}
                style={{
                  data: { fill: "white" },
                  labels: { fill: "white" },
                }}
                labelComponent={
                  <VictoryTooltip
                    dy={-35}
                    cornerRadius={0} // Отключить закругление углов
                    style={{ fill: "white", fontSize: 15, fontFamily: "Arial" }}
                    flyoutStyle={{ fill: "#2d2d2d", stroke: "transparent" }}
                    pointerLength={0} // Отключить стрелку
                    pointerWidth={0} // Отключить стрелку
                  />
                }
              />

              <VictoryScatter
                data={points2}
                size={({ active }) => (active ? 3 : 1)}
                style={{
                  data: { fill: "white" },
                }}
              />

              <VictoryLegend
                x={60}
                y={530}
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
                //     labels={({ datum }) =>
                //   `latency: ${datum.overall_censorship_latency.toFixed(4)}`
                // }
                labelComponent={<VictoryTooltip />}
              />
              <VictoryLine
                alignment="middle"
                style={{ data: { stroke: "#1e90ff" } }}
                // labels={({ datum }) => datum.y}
                data={latencyState}
                x="range_date"
                y="overall_censorship_latency"
                //     labels={({ datum }) =>
                //   `without_latency: ${datum.overall_censorship_latency_without_lido_censorship.toFixed(4)}`
                // }
                labelComponent={<VictoryTooltip />}
              />

              <VictoryAxis
                dependentAxis
                // tickFormat={(t) => `${t}%`}
                style={{
                  tickLabels: { fontSize: 15, fill: "#FFFFFF" },
                  axisLabel: { padding: 30 },
                }}
                label="LATENCY"
                // axisLabelComponent={<VictoryLabel dy={20} />}
                tickFormat={(t) => `${t}s`}
                axisLabelComponent={
                  <VictoryLabel
                    style={[{ fill: "#FFFFFF", fontSize: 13 }]}
                    dy={-220}
                    // padding={100}
                    angle={360}
                  />
                }
              />
              <VictoryAxis
                tickFormat={(t, index, ticks) => {
                  if (ticks.length <= 8) {
                    return t;
                  } else {
                    const date = getDateOnStr(t);
                    const month = date.getMonth();
                    const year = date.getFullYear();
                    const monthNames = [
                      "Jan",
                      "Feb",
                      "Mar",
                      "Apr",
                      "May",
                      "Jun",
                      "Jul",
                      "Aug",
                      "Sep",
                      "Oct",
                      "Nov",
                      "Dec",
                    ];
                    if (index === 0 || index === ticks.length - 1) {
                      return `${year}`;
                    } else if (month !== prevMonth) {
                      prevMonth = month;
                      return `${monthNames[month]}`;
                    } else {
                      return "";
                    }
                  }
                }}
                style={{ tickLabels: { fontSize: 10, fill: "#FFFFFF" } }}
                tickValues={tickValues}
                label="DATE"
                axisLabelComponent={
                  <VictoryLabel
                    dy={-10}
                    dx={250}
                    style={[{ fill: "#FFFFFF", fontSize: 15 }]}
                  />
                }
              />
            </VictoryChart>
          </div>
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
            We also compute a modified version of the Censorship Latency metric
            by assuming that the Lido validators were completely non-censoring.
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
