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
  const height = 800;
  return (
    <div>
      <div class="h3 w-1/6 bg-indigo-500 px-8 py-6 text-white text-right bg-center font-extrabold rounded-full">
        <button type="button" onClick={handleClick}>
          {buttonPoolState}
        </button>
      </div>

      <div class="h3 text-center">
      <h3>Share of all transactions (OFAC - NON OFAC transactions)</h3>
      </div>

      <div
        style={{
          height: height,
          width: width,
        }}
        class=" mx-auto"
      >
        <VictoryChart
          height={130}
          width={700}
          padding={{bottom:100,left:100}}
          label="Share of all transactions (OFAC - NON OFAC transactions)"
        >
        <VictoryBar
            horizontal
            barWidth={8}
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
    </div>
  );
}

export default PoolChart;