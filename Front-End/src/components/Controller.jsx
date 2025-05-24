import React from 'react';
import { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

function Controller({ Type = null, items = [] }) {
    const text = {
        ctg: "Categories",
        ctr: "Countries",
        chn: "Channels"
    }
    const [isLoading, setLoading] = useState(true);
    const [isError, setError] = useState(null);
    const [isUpdating_mnu, setIsUpdating_mnu] = React.useState(false);
    const [message, setMessage] = useState([]);
    const [status, setStatus] = useState('Stopped');
    const [interval, setInterval] = useState(0);
    let msg_successfull_class = "bg-success text-light text-center rounded text-wrap p-1";
    let msg_failed_class = "bg-danger text-light text-center rounded text-wrap p-1";

    // Function to Update Data Manually
    const handleUpdateManual = async () => {
        setIsUpdating_mnu(true);
        try {
            const res = await fetch(`http://localhost:5000/update_data`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ "Type":Type })
            });
          const data = await res.json();
          if (data.status === 'success') {
            setMessage([msg_successfull_class, 'Data updated successfully']);
          } else {
            setMessage([msg_failed_class, 'Update Failed']);
          }
        } catch {
            setMessage([msg_failed_class, 'Update Failed']);
        }
        setIsUpdating_mnu(false);
        setTimeout(() => setMessage([]), 3000);
    };

    // Function to handle the interval update
    const handleUpdateInterval = async (value) => {
        const interval = Number(value);
        setInterval(interval);
        try {
            const res = await fetch(`http://localhost:5000/set_interval/${interval}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ "Type":Type })
            });
          const data = await res.json();
          if (data.status === 'success') {
            setMessage([msg_successfull_class, 'Interval updated successfully']);
          } else {
            setMessage([msg_failed_class, 'Failed to change interval !']);
          }
        } catch {
            setMessage([msg_failed_class, 'Failed to change interval !']);
        }
        setTimeout(() => setMessage([]), 3000);
    };

    // Function to toggle the auto-updater
    const toggleAutoUpdater = async () => {
        try {
            const res = await fetch(`http://localhost:5000/toggle_updater`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ "Type":Type })
            });
          const data = await res.json();
          if (data.status === true) {
            setMessage([msg_successfull_class, 'Updater toggled successfully']);
            setStatus(status === 'Stopped' ? 'Running' : 'Stopped');
          } else {
            setMessage([msg_failed_class, 'Failed to toggle updater !']);
          }
        } catch {
            setMessage([msg_failed_class, 'Failed to toggle updater !']);
        }
        setTimeout(() => setMessage([]), 3000);
    };

    // Fetch data from the API (Interval and Status)
    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(`http://localhost:5000/get_status`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ "Type":Type })
                });
              const data = await res.json();
              if (data.status === 'error') {
                setError(true);
              } else {
                setStatus(data.status === true ? 'Running' : 'Stopped');
                setInterval(data.interval);
              }
            } catch {
                setError(true);
            } finally {
                setLoading(false);
            }
        };
      
        fetchData();
    }, []);
    

    return (
        <>
            {(isLoading !== true && isError !== true && Type !== null && items.length>0 && items.includes(Type)) ? (
                <div className='container-fluid w-100'>
                    <div className='row bg-info mt-1 mb-2 rounded p-2'>
                        <h1 className="h4 text-light text-center text-wrap"> {text[Type]} Updater Management </h1>
                    </div>

                    <div className='row text-center'>
                        <h6 className="text-wrap text-light">Automatic Updater is <span className={`badge bg-${status === "Stopped" ? "danger" : "info"} rounded text-wrap`}>{status}</span></h6>
                    </div>

                    <div className='row text-center'>
                        {status === "Running" ? (
                            <div className="form-group text-center">
                                <label htmlFor={`${Type}-au-inteval`} className="text-light text-wrap">Interval (In minutes)</label>
                                <div className="input-group mb-3">
                                    <div className="input-group-prepend">
                                        <button className="form-control btn btn-danger" onClick={toggleAutoUpdater}>Stop</button>
                                    </div>
                                    <input value={interval} type="number" className="form-control" onChange={(e) => handleUpdateInterval(e.target.value)} />
                                </div>
                                <button onClick={handleUpdateManual} className="btn btn-primary mb-2 mt-1 text-wrap" disabled={isUpdating_mnu}> 
                                    {isUpdating_mnu ? <div><span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...</div> : "Update Data Manually"}
                                </button>
                            </div>
                        ):(
                            <div className="form-group text-center">
                                <div className="btn-group" role="group" aria-label="Basic example">
                                <button className="form-control btn btn-primary border" onClick={toggleAutoUpdater}>Start</button>
                                    <button onClick={handleUpdateManual} className="form-control btn btn-primary text-wrap border" disabled={isUpdating_mnu}> 
                                        {isUpdating_mnu ? <div><span className="spinner-border spinner-border-sm text-wrap" role="status" aria-hidden="true"></span> Updating...</div> : "Update Data Manually"}
                                    </button>
                                </div>
                            </div>
                        )}
                        
                    </div>

                    <div className='row text-center mt-2'>
                        {message.length > 0 && <span className={message[0]}>{message[1]}</span>}
                    </div>
                </div>
            ) : (
            <h1 className='text-light text-center'>{isLoading === true ? "Loading ..." : "Error"}</h1>
            )}
        </>
    );
}


export default Controller;