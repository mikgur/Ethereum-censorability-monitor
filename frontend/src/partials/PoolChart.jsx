import React, { useEffect, useState } from "react";
import {
  VictoryBar,
  VictoryChart,
  VictoryLabel,
  VictoryGroup,
  VictoryAxis,
  VictoryContainer,
  VictoryLegend,
} from "victory";


import { getAllPool } from "./DataAccessLayer";

function PoolChart() {
  const [poolState, setPoolState] = useState();
  const [poolPeriodState, setPoolPeriodState] = useState(true);

  const [buttonPoolState, setButtonPoolState] = useState(
    "Switch to last month"
  );

  useEffect(() => {
    getPoolData("last_week")
  }, []);

  const getPoolData = async (period) => {
    const data = await getAllPool(period);
    setPoolState(data.data);
  };

  const handleClick = () => {
    setPoolPeriodState((poolPeriodState) => !poolPeriodState);
    if (poolPeriodState == false) {
      getPoolData("last_month");
      setButtonPoolState("Switch to last week");
    } else {
      getPoolData("last_week");
      setButtonPoolState("Switch to last month");
    }
  };

  const width = 1800;
  const height = 600;
  return (
    <div>


      <div class="h2 text-center">
      <h3>Lido vs rest ratio</h3>
      </div>

      <div
        style={{
          height: height,
          width: width,
        }}
        class=" mx-auto"
      >
        <VictoryChart
          height={150}
          width={700}
          padding={{bottom:50,left:100,right:100,top:50}}
          label="Lido vs rest ratio"
        >
        <VictoryBar
            horizontal
            barWidth={10}
            alignment="middle"
            style={{ data: { fill: "#1e90ff" } }}
            data={poolState}
            x="pool"
            y="ratio"
        />
          <VictoryAxis
            dependentAxis
            tickFormat={(t) => `${t}%`}
            style={{ tickLabels: { fontSize: 11, fill: "#FFFFFF" } }}
            label="RATIO"
            axisLabelComponent={
              <VictoryLabel
                style={[{ fill: "#FFFFFF", fontSize: 17 }]}
                padding={100}
              />
            }
          />
          <VictoryAxis
            style={{ tickLabels: { fontSize: 11, fill: "#FFFFFF" } }}
            label="POOL"
            axisLabelComponent={
              <VictoryLabel
                dy={-50}
                style={[{ fill: "#FFFFFF", fontSize: 17 }]}
              />
            }
          />
        </VictoryChart>
      </div>
      
      <div class="h3 mb-4  px-6 py-3 text-white text-center bg-center font-extrabold rounded-full">
        <button type="button" onClick={handleClick} class="bg-sky-500 hover:bg-cyan-600 bg-center font-extrabold rounded-full px-6 py-3">
          {buttonPoolState}
        </button>
      </div>
    </div>
  );
}

export default PoolChart;