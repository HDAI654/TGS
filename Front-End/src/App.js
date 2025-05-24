import React from 'react';
import Manager from './components/Manager';
import TableTabs from './components/TableTabs';
import "bootstrap/dist/css/bootstrap.min.css";

function App() {
  return (
    <div>
      <Manager />
      <div className="row mt-5">
        <TableTabs items={['ctg', 'ctr', 'chn']} />
      </div>
    </div>
  );
}

export default App;
