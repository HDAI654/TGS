import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import Table from './Table';


function TableTabs({ items = [] }) {
    const text = {
        ctg: "Categories",
        ctr: "Countries",
        chn: "Channels"
    }
    
    return (
        <>
            {(items.length>0) ? (
                <div className="container">
                    <ul className="nav nav-tabs mt-2" id="myTab" role="tablist">
                        {items.map((item, index) => (
                            <li key={index} className="nav-item" role="presentation">
                                <button className="nav-link" id={item + "-tab"} data-bs-toggle="tab" data-bs-target={"#" + item + "-content"} type="button" role="tab" aria-controls={item + "-content"} aria-selected="true">{text[item]}</button>
                            </li>
                        ))}
                    </ul>
                    <div className="tab-content" id="myTabContent">
                        {items.map((item, index) => (
                            <div key={index} className="tab-pane fade show" id={item + "-content"} role="tabpanel" aria-labelledby={item + "-tab"}>
                                <div className="table-responsive">
                                    <Table Type={item} items={items} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
            <h1 className='text-light text-center'>Error</h1>
            )}
        </>
    );
}


export default TableTabs;