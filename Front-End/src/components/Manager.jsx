import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import Controller from './Controller';

function Manager() {
    const items = ["ctg", "ctr", "chn"]

    return ( 
        <div className='container-fluid bg-dark'>
            <div className='row'>
                {items.map((v, i) => (
                    <div key={i} className='col-lg-4 col-md-4 col-sm-12 p-1 border border-light'>
                        <Controller Type={v} items={items} />
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Manager;
