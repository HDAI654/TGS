import React from 'react';
import { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

function Table({ Type = null, items = [] }) {
    const [isLoading, setLoading] = useState(true);
    const [isError, setError] = useState(null);
    const [data, setData] = useState(null);

    // Fetch data from the API (Interval and Status)
    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await fetch(`http://localhost:5000/get_data`, {
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
                setData(data.data);
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
            {(isLoading !== true && isError !== true && Type !== null && items.length>0 && items.includes(Type) && data !== null) ? (
                <div className='container-fluid w-100'>
                    <table className="table table-sm table-dark table-hover">
                        <thead>
                            <tr>
                                {Array.isArray(data) && data.length > 0 && Object.keys(data[0]).map((key) => (
                                    <th key={key}>{key}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {Array.isArray(data) && data.map((row, rowIndex) => (
                                <tr key={rowIndex}>
                                    {Object.values(row).map((value, colIndex) => {
                                        const isEmojiColumn = Object.keys(data[0])[colIndex] === "emoji";
                                        return (
                                            <td
                                                key={colIndex}
                                                style={isEmojiColumn ? { fontFamily: "'Noto Color Emoji', sans-serif" } : {}}
                                            >
                                                {String(value)}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
            <h1 className='text-light text-center'>{isLoading === true ? "Loading ..." : "Error"}</h1>
            )}
        </>
    );
}


export default Table;