import React, { useEffect, useState } from "react";
import {
  VictoryBar,
  VictoryChart,
  VictoryLabel,
  VictoryAxis,
  VictoryContainer,
  VictoryTooltip,
} from "victory";

import { getAllPool } from "./DataAccessLayer";

const PERIODS = [
  { value: 'last_week', label: 'Last week', buttonLabel: '1w' },
  { value: 'last_month', label: 'Last month', buttonLabel: '1m' },
  { value: 'last_half_year', label: 'Last six months', buttonLabel: '6m' },
  { value: 'last_year', label: 'Last year', buttonLabel: '1y' },
]

function Button({ period, currentPeriod, setPeriod }) {
  return (
    <button
      onClick={() => setPeriod(period.value)}
      style={{
        transition: "background 0.3s ease",
        background: period.value === currentPeriod ? "#319795" : "#6b7280",
        color: period.value === currentPeriod ? "white" : "#d1d5db",
        // borderRadius: "5px",
        padding: "5px 15px",
      }}
    >
      {period.buttonLabel}
    </button>
  );
}




function VolumeChart() {
  const [poolState, setPoolState] = useState();
  const [currentPeriod, setCurrentPeriod] = useState('last_half_year');


  useEffect(() => {
    getPoolData("last_half_year");
  }, []);

  useEffect(() => {
    getPoolData(currentPeriod);
  }, [currentPeriod]);

  const getPoolData = async (period) => {
    const data = await getAllPool(period);
  
    let outherTotalShare = 0;
  
    const filteredData = [];
    let sum_percent = 0
    data.data.forEach(d => {
      if (d.total_share < 0.5) {
        outherTotalShare += d.total_share;
      } else if (d.total_share > 0.5) {
        filteredData.push(d);
      }
      sum_percent = sum_percent + d.total_share
    });
    
    console.log(sum_percent)
    const sortedData = filteredData.sort((a, b) => a.total_share - b.total_share);

    if (outherTotalShare > 0) {
      sortedData.unshift({ pool: "Other", total_share: outherTotalShare });
    }
  
    setPoolState(sortedData);
  };

  const getChartWidth = () => {
    const windowWidth = window.innerWidth;
  
    if (windowWidth < 640) return windowWidth - 40;
    if (windowWidth < 768) return windowWidth - 40; // same as sm for better transition
    if (windowWidth < 1024) return windowWidth - 40;
    if (windowWidth < 1280) return 600;
    return 800;
  };
  
  const chartWidth = getChartWidth() * 1.2;
  const chartHeight = chartWidth * 0.7;

  return (
    <div>
      <div class="h3 text-center">
        <h4>
          Volume Lido/Non-Lido(
          {PERIODS.find((p) => p.value === currentPeriod).label})
        </h4>
      </div>
      <br></br>
      <div class="flex flex-wrap space-x-0 justify-center mx-8">
        <div class="w-full sm:w-3/4 md:w-2/3 lg:w-1/2 xl:w-1/3 h-auto">
          <div class="flex justify-center overflow-hidden text-center mb-4">
            {PERIODS.map((period) => (
              <Button
                period={period}
                currentPeriod={currentPeriod}
                setPeriod={setCurrentPeriod}
              />
            ))}
          </div>
          <VictoryChart
             height={chartHeight}
             width={chartWidth}
            padding={{ bottom: 100, left: 100, right: 100, top: 50 }}
            label="Lido vs rest ratio"
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
            <VictoryBar
                horizontal
                barWidth={10}
                alignment="middle"
                data={poolState}
                x="pool"
                y="total_share"
                labels={({ datum }) => `Total share: ${datum.total_share.toFixed(4)}`}
                style={{ labels: { fill: "white" }, data: { fill: "#1e90ff" } }}
                labelComponent={
                  <VictoryTooltip
                    cornerRadius={0}
                    style={{ fill: "white", fontSize: 17, fontFamily: "Arial" }}
                    flyoutStyle={{ fill: "#2d2d2d", stroke: "transparent" }}
                    pointerLength={0}
                    pointerWidth={0}
                  />
                }
              />
            {/* </VictoryGroup> */}
            <VictoryAxis
              dependentAxis
              // tickFormat={(t) => `${t}%`}
              style={{ tickLabels: { fontSize: 11, fill: "#FFFFFF" } }}
              label="Volume"
              axisLabelComponent={
                <VictoryLabel
                  style={[{ fill: "#FFFFFF", fontSize: 17 }]}
                  padding={100}
                />
              }
            />
            <VictoryAxis
              style={{ tickLabels: { fontSize: 15, fill: "#FFFFFF" } }}
              label="POOL"
              axisLabelComponent={
                <VictoryLabel
                  dy={-60}
                  style={[{ fill: "#FFFFFF", fontSize: 17 }]}
                />
              }
            />
          </VictoryChart>
        </div>

        <div class=" desktop:w-[600px] tablet:w-[400px] tablet:h-[300px] laptop:w-[300px]  mr-48">
          <p class="desktop:text-xl desktop:text-xl indent-8">
            We calculate Censorship Resistance Index for Lido at all and compare
            it to all other known pools in total.
          </p>
          <br></br>
          <p>Example of metric calculation:</p>
          <br></br>
          <p>A = OFAC Compliance Ratio calculated for pool N in total</p>
          <p>
            B = NON-OFAC Compliance Ratio calculated for the pool N in total
          </p>
          <p>Censorship Resistance Index for pool N = B / A</p>
        </div>
      </div>
    </div>
  );
}

export default VolumeChart;
