import React from 'react';
import { Button } from 'reactstrap';

import { useEffect, useState } from 'react';
import { Link, useHistory, useParams } from "react-router-dom";

import BarChart from 'react-bar-chart';
import { PieChart } from 'react-minimal-pie-chart';
import { Doughnut } from 'react-chartjs-2';
import { Bar } from 'react-chartjs-2';
import DataTable from 'react-data-table-component';

import moment from 'moment';


function SessionListItem(props) {
    const sessionid = props.sessionid;
    const handleSessionClicked = props.handleSessionClicked;
    const courseStats = props.courseStats;
    
    return (
       <li key={sessionid} id={sessionid} onClick={() => handleSessionClicked(sessionid)}>
            <span style={{ padding: "5px" }}>
                { moment(courseStats.session_info[sessionid].date - 1000).format("YYYY-MM-DD") }
            </span>
            {/*
            <span style={{ padding: "5px" }}>
                { sessionid }
            </span>
            */}
            <tt>{ sessionid }</tt>
            <span style={{ padding: "5px"}}/>
            {/*
            <span style={{ padding: "1px", "text-align": "right", monospace: true }}>
                { '- ' + courseStats.session_info[sessionid].score.toString() + '%' }
            </span>
            */}
            <tt>{ courseStats.session_info[sessionid].score.toString().padStart(4) }</tt>
        </li> 

    );
};

// Session statistics display ...
function StatsDiv(props) {

    const courseStats = props.courseStats;
    const scoreHistory = props.scoreHistory;
    const handleSessionClicked = props.handleSessionClicked;

	return (
            <div style={{ float: 'top', width: '100%', height: '200px'}}>
                <span className="column" style={{ float: "left", margin: '10px', width: "20%", height: '100%', padding: '10px', 'border-radius': '10px', background: 'white'}}>
                    <h5>total questions answered</h5>
                        <Doughnut
                        legend={ {display: true} }
                        data={ {
                            labels: ['answered', 'unanswered'],
                            datasets: [ {
                                data: [ courseStats.answered, courseStats.total - courseStats.answered ],
                                backgroundColor: ['green', 'lightgray']
                            } ]
                        } }
                    />
                        
                </span>
                <span className="column" style={{ float: "left", margin: '10px', width: "35%", height: '100%', padding: '10px', 'border-radius': '10px', background: 'white'}}>
                    <h5>quiz scores</h5>
                    <Bar
                        legend={ {display: false} }
                        width={ '100%' }
                        height={ '25' }
                        data={ {
                            labels: scoreHistory.map((score, ix) => ix),
                            datasets: [ {
                                data: scoreHistory
                            } ]
                        } }
                    />
                        
                </span>
                <span className="column" style={{ float: "left", margin: '10px', width: "33%", height: '100%', padding: '10px 10px 10px 10px', 'border-radius': '10px', background: 'white', 'font-size': '10px'}}>
                    <h5>last quiz results</h5>
                    { courseStats.sessionids !== undefined &&
                        courseStats.sessionids.slice(0).reverse().slice(0,10).map((sessionid, session_index) =>
                            <SessionListItem
                                sessionid={ sessionid }
                                courseStats={ courseStats }
                                handleSessionClicked={handleSessionClicked }
                            />
                        )
                    }
                </span>
            </div>
	);
}

export default StatsDiv;
