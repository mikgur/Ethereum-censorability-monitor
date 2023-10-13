import React from 'react';

import Header from '../partials/Header';
import PageIllustration from '../partials/PageIllustration';
import HeroHome from '../partials/HeroHome';
import VisChart from '../partials/VisChart';
import RatioChart from '../partials/RatioChart';
import PoolChart from '../partials/PoolChart';
import LatencyChart from '../partials/LatencyChart';
import CensoredLatencyChart from '../partials/CensoredLatencyChart';
import Percent from '../partials/Percent';
import VolumeChart from '../partials/VolumeChart';
import Description from '../partials/Description';

function Home() {
  return (
    <div className="flex flex-col min-h-screen overflow-hidden">
      {/*  Site header */}
      <Header />

      {/*  Page content */}
      <main className="grow">
        <div className="relative max-w-6xl mx-auto h-0 pointer-events-none" aria-hidden="true">
          <PageIllustration />
        </div>
        <HeroHome />
        <LatencyChart />
        <div style={{height: 100, weight: 200}}></div>
        <Percent />
        <div style={{height: 100, weight: 200}}></div>
        <CensoredLatencyChart />
        <div style={{height: 200, weight: 200}}></div>
        <VisChart />
        <div style={{height: 300, weight: 200}}></div>
        <RatioChart />
        <div style={{height: 300, weight: 200}}></div>
        <VolumeChart />
        <div style={{height: 300, weight: 200}}></div>
        <PoolChart />
        <div style={{height: 100, weight: 200}}></div>
        <Description />
      </main>
    </div>
  );
}

export default Home;