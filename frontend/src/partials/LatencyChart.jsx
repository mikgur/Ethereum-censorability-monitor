import React, { useEffect, useState } from "react";
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

import { getLatency } from "./DataAccessLayer";

function LatencyChart() {
  const [latencyState, setLatencyState] = useState();
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [filteredData, setFilteredData] = useState([]);


  useEffect(() => {
    getLatencyData();
  }, []);

  const getLatencyData = async () => {
    const data = await getLatency();
    setLatencyState(data.data.slice(-8));
  };

  useEffect(() => {
        const filtered = latencyState.filter(item => {
            let itemDate = new Date(item.date);
            return itemDate >= startDate && itemDate <= endDate;
        });
        setFilteredData(filtered);
    }, [startDate, endDate, latencyState]);
  // const handleStartDateChange = (date) => {
  //   if (date.getDay() === 1) {
  //     setStartDate(date);
  //   }
  // };

  // const handleEndDateChange = (date) => {
  //   if (date.getDay() === 0) {
  //     setEndDate(date);
  //   }
  // };

  // // Фильтрация данных на основе выбранных дат
  // const filteredData = data.filter((item) => {
  //   if (!startDate || !endDate) {
  //     return true; // Вернуть все данные, если даты не выбраны
  //   }
  // });

  return (
    <div>
      <div class="h3 text-center">
        <h3>Average Censorship Latency</h3>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0 justify-center mx-8">
      <div className="datePickerContainer">
                <DatePicker
                    selected={startDate}
                    onChange={date => setStartDate(date)}
                    selectsStart
                    startDate={startDate}
                    endDate={endDate}
                />
                <DatePicker
                    selected={endDate}
                    onChange={date => setEndDate(date)}
                    selectsEnd
                    endDate={endDate}
                    minDate={startDate}
                />
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
              data={filteredData}
              x="start_date"
              y="overall_censorship_latency_without_lido_censorship"
            />
            <VictoryLine
              alignment="middle"
              style={{ data: { stroke: "#1e90ff" } }}
              // labels={({ datum }) => datum.y}
              data={filteredData}
              x="start_date"
              y="overall_censorship_latency"
            />
            <VictoryScatter
              data={filteredData}
              x="start_date"
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
              data={filteredData}
              x="start_date"
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
