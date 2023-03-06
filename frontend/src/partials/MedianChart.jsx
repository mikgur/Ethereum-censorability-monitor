import React, { useEffect, useState } from "react";
import {
  VictoryBar,
  VictoryChart,
  VictoryLabel,
  VictoryGroup,
  VictoryAxis,
  VictoryContainer,
  VictoryLegend,
  VictoryArea,
  VictoryTheme,
  VictoryLine,
  VictoryScatter,
  VictoryTooltip,
} from "victory";

import { getMedian, getPercent } from "./DataAccessLayer";

function MedianChart() {
  const [medianState, setMedianState] = useState();
  const [percentState, setPercentState] = useState();

  useEffect(() => {
    getMedianData();
  }, []);

  useEffect(() => {
    getPercentData();
  }, []);

  const getMedianData = async () => {
    const data = await getMedian();
    setMedianState(data.data);
  };

  const getPercentData = async () => {
    const data = await getPercent();
    setPercentState(data.data);
  };


  return (
    <div>
      <div class="h3 text-center space-x-30 ">
        <h3>
          <b>
            Of all Non-OFAC compliant transactions,{" "}
            {46}% were censored at 
            least once. Lido validators were involved in censoring of{" "}
            {21}% of Non-OFAC
            compliant transactions during last 30 days.
          </b>
        </h3>
      </div>
      <div style={{height: 100, weight: 200}}></div>
      <div class="h3 text-center">
        <h3>Median Censorship Latency</h3>
      </div>

      <br></br>
      <div class="flex flex-wrap space-x-0 justify-center">
        <div class="desktop:w-[1200px] desktop:h-[700px] uwdesktop:w-[1600px] uwdesktop:h-[900px] laptop:w-[700px]  laptop:h-[700px] ml-24">
          <VictoryChart
            height={600}
            width={600}
            padding={{ bottom: 130, left: 100, right: 100, top: 50 }}
            minDomain={{ y: 0 }}
            maxDomain={{ y: 40 }}
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
                  name: "Median Censorship Latency ",
                  symbol: { fill: "#1e90ff" },
                  labels: { fill: "#FFFFFF" },
                },
                {
                  name: "Median Censorship Latency if Lido was\n completely non-censoring ",
                  symbol: { fill: "#c43a31" },
                  labels: { fill: "#FFFFFF" },
                },
              ]}
            />
            <VictoryLine
              alignment="middle"
              style={{ data: { stroke: "#c43a31" } }}
              data={medianState}
              x="start_date"
              y="median_censorship_latency_without_lido_censorship"
            />
            <VictoryLine
              alignment="middle"
              style={{ data: { stroke: "#1e90ff" } }}
              // labels={({ datum }) => datum.y}
              data={medianState}
              x="start_date"
              y="median_censorship_latency"
            />
            <VictoryScatter
              data={medianState}
              x="start_date"
              y="median_censorship_latency"
              size={7}
              style={{
                data: { fill: "white" },
                labels: { fill: "white" },
              }}
              labels={({ datum }) =>
                `latency: ${datum.median_censorship_latency.toFixed(4)}`
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
              data={medianState}
              x="start_date"
              y="median_censorship_latency_without_lido_censorship"
              size={7}
              style={{
                data: { fill: "white" },
                labels: { fill: "white" },
              }}
              labels={({ datum }) =>
                `latency: ${datum.median_censorship_latency_without_lido_censorship.toFixed(
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
              style={{ tickLabels: { fontSize: 19, fill: "#FFFFFF" } }}
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
            <b>Median Censorship Latency </b>
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            The Censorship Latency Median metric is calculated as the median
            waiting time for non-OFAC compliant transactions{" "}
            <b class="text-red-600">that were censored before being included in a block.</b> We use a
            binary classifier to predict the number of blocks for which non-OFAC
            compliant transactions were not included due to censorship, and then
            calculate the median waiting time for these transactions.
          </p>
          <br></br>
          <p class="desktop:text-xl uwdesktop:text-2xl">
            <b>
            Median Censorship Latency if Lido was completely non-censoring for
              censored transactions 
            </b>
          </p>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            This metric is a modified version of the Censorship Latency Median
            metric, which assumes that Lido validators were completely
            non-censoring. This metric measures the median waiting time for
            non-OFAC compliant{" "}
            <b class="text-red-600">
              transactions that were censored before being included in a block.
            </b>{" "}
            Similar to the Censorship Latency Median metric, we use a binary
            classifier to predict the number of blocks for which non-OFAC
            compliant transactions were not included due to censorship, and then
            calculate the median waiting time for these transactions.
          </p>
          <br></br>
          <p class="desktop:text-xg uwdesktop:text-xl indent-8">
            For both of these metrics, the waiting time is measured in the
            number of blocks that the transaction was censored before being
            included in a block, multiplied by 12 seconds (the average time it
            takes to mine a block on the Ethereum network).
          </p>
          
        </div>
      </div>
    </div>
  );
}

export default MedianChart;
