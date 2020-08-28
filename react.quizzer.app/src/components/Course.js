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

const customStyles = {
    headRows: {
        style: {
            maxHeight: '10px',
            paddingTop: '5px',
            paddingBottom: '5px',
            paddingLeft: '20px',
            paddingRight: '20px'
        }
    },
    rows: {
        style: {
            maxHeight: '10px',
            paddingTop: '5px',
            paddingBottom: '5px',
            paddingLeft: '20px',
            paddingRight: '20px'
        }
    },
    headCells: {
        style: {
            margin: '20px',
            maxHeight: '10px',
            paddingTop: '5px',
            paddingBottom: '5px',
            paddingLeft: '20px',
            paddingRight: '20px'
        }
    },
    cells: {
        style: {
            paddingTop: '5px',
            paddingBottom: '5px',
            paddingLeft: '10px',
            paddingRight: '10px'
        }
    }
}

const conditionalRowStyles = [
    {
        when: row => row.average > 79,
        style: {
            backgroundColor: 'lightgreen',
            maxHeight: '10px',
        }
    },
    {
        when: row => row.average < 80 && row.average > 59,
        style: {
            backgroundColor: 'orange',
            maxHeight: '10px',
        }
    },
    {
        when: row => row.total > 0 && row.average < 60,
        style: {
            backgroundColor: 'pink',
            maxHeight: '10px',
        }
    },
    {
        when: row => row.total === 0,
        style: {
            backgroundColor: 'lightyellow',
            maxHeight: '10px',
        }
    }
]

function QuestionRow(props) {
    return (
        <div>
            <Link
                key={ props.questionId }
                to={ "/courses/" + props.courseName + '/questions/' + props.questionId }>
                { props.questionId }
            </Link>
            total: 0
            correct: 0
            incorrect: 0
        </div>
    );
}

// THE FULL PAGE ABOUT A COURSE
function CoursePage() {

    const [questionList, setQuestionList] = useState([]);
    const [courseStats, setCourseStats] = useState({});
    const [allTableData, setAllTableData] = useState([]);
    const [tableData, setTableData] = useState([]);
    const [chartOptions, setChartOptions] = useState({});
    const [scoreHistory, setScoreHistory] = useState([]);
    const [searchText, setSearchText] = useState(null);
    const [searchTextTmp, setSearchTextTmp] = useState(null);
    const [filteredRows, setFilteredRows] = useState(null);
    const [cachedStats, setCachedStats] = useState(null);
    const history = useHistory();

    const chartMargin = {top: 20, right: 20, bottom: 30, left: 40};

	let { courseName } = useParams();
    const tableColumns = [
        {name: 'questionid', selector: 'questionid', compact: true},
        {name: 'section', selector: 'section', compact: true},
        {name: 'average', selector: 'average', compact: true, right: true, sortable: true},
        {name: 'total attempts', selector: 'total', compact: true, right: true, sortable: true},
        {name: 'correct', selector: 'correct', compact: true, right: true},
        {name: 'incorrect', selector: 'incorrect', compact: true, right: true}
    ];

    const handleOnChangeSearch = (e) => {
        console.log(e.target.value);
        setSearchTextTmp(e.target.value);
    };

    const handleSearchSubmit = (e) => {
        //console.log(e);
        //console.log(e.target.value);
        setSearchText(searchTextTmp);
    };

    const handleQuestionRowClicked = (row) => {
        console.log(row);
        const rowQuestionId = row.questionid;
        const questionUrl = '/courses/' + courseName + '/questions/' + rowQuestionId;
        window.location = questionUrl;
    };

    const handleSessionClicked = (sessionid) => {
        console.log(sessionid)
        const sessionUrl = '/sessions/' + sessionid;
        window.location = sessionUrl;
    };

    useEffect(() => {
        //let isMounted = true;
        console.log('coursepage useeffect ...');

        const fetchQuestionList = async () => {
            const courseApiUrl = '/api/courses/' + courseName;
            const newQuestionList = await fetch(courseApiUrl + '/questions')
                .then(res => res.json());
            setQuestionList(newQuestionList);
        };

        const fetchCourseStats = async () => {
            const courseStatsUrl = '/api/stats/' + courseName;
            const newStats = await fetch(courseStatsUrl)
                .then(res => res.json());
            setCourseStats(newStats);
            setScoreHistory(newStats.score_history)

            // build the rows for the table ...
            let newTableData = [];
            for (let i=0; i<newStats.questionlist.length; i++) {
                const qid = newStats.questionlist[i];
                console.log(qid);
                let thisRowData = newStats.questions[qid];
                thisRowData.id = i;
                if ( thisRowData.total > 0 ) {
                    thisRowData.average = (thisRowData.correct / thisRowData.total) * 100;
                } else {
                    thisRowData.average = 0;
                };
                console.log(thisRowData);
                newTableData.push(thisRowData);
            }

            /*
            if ( searchText !== null && searchText !== "") {
                newTableData = newTableData.filter(function(row, index, arr) {
                    if ( row.section === undefined ) {
                        return false;
                    }; 
                    return row.section.includes(searchText);
                    //console.log(row);
                    //return true;
                });
            };
            */

            setTableData(newTableData);
            setAllTableData(newTableData);

        };

        /*
        if ( questionList === [] ) {
            fetchQuestionList();
        }
        if ( courseStats === [] || tableData === [] ) {
            fetchCourseStats();
        }
        */
        fetchQuestionList();
        fetchCourseStats();

        /*
        let newTableData = [];
        for (let i=0; i<questionList.length; i++) {
            const qid = questionList[i];
            let thisRowData = {...questionStats[qid]};
            newTableData.push(thisRowData);
        }
        setTableData([...newTableData]);
        */

        return () => {
            console.log('cleanup');
        };
    }, [courseName]);

    // filter the table rows if user types in the search box
    useEffect(() => {
        let startList;
        if ( searchText === null || searchText === "") {
            startList = [...allTableData];
        } else {
            startList = [...tableData];
        }

        if ( searchText !== null && searchText !== "") {
            let newTableData = startList.filter(function(row, index, arr) {
                if ( row.section === undefined ) {
                    return false;
                }; 
                return row.section.includes(searchText);
                //console.log(row);
                //return true;
            });
            setTableData(newTableData);
        } else {
            setTableData(startList);
        }

    }, [searchText]);

    const startQuiz = () => {
        //<Link to={ "/courses/" + courseName + '/quiz' }>start quiz</Link>
        const quizUrl = '/courses/' + courseName + '/quiz';
        history.push(quizUrl)
    };

	return (
		<div style={{ 'margin-top': '30px' }}>
        	<h2>{ courseName.replace(/_/g, ' ') }</h2>
            <hr/>

            <div style={{ }}>
                <span style={{ padding: "10px" }}>
                    <Button onClick={startQuiz} color="warning">start quiz</Button>
                </span>
                <span style={{ padding: "10px" }}>
                    <Button onClick={startQuiz} color="danger">start test</Button>
                </span>
            </div>
            <hr/>

            <div style={{ float: 'top', width: '100%', height: '200px'}}>
                <span className="column" style={{ float: "left", margin: '10px', width: "20%", height: '100%', padding: '10px', 'border-radius': '10px', background: 'white'}}>
                    <h5>total answered</h5>
                        {/*
                        <PieChart
                            label={ (labelRenderProps: LabelRenderProps) => 
                                'stuff' 
                            }
                            data={ [ 
                                { key: 'answered', title: 'answered', value: courseStats.answered, color: 'green' },
                                { key: 'unanswered', title: 'unanswered', value: courseStats.total - courseStats.answered, color: 'gray' }
                            ] }
                            />
                        */}
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
                    <h5>session scores</h5>
                        {/*
                        <BarChart
                            margin={ chartMargin }
                            ylabel='score'
                            width={ 600 }
                            height={ 200 }
                            data={ scoreHistory }
                            />
                        */}
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
                <span className="column" style={{ float: "left", margin: '10px', width: "33%", height: '100%', padding: '5px 10px 10px 30px', 'border-radius': '10px', background: 'white', 'font-size': '10px'}}>
                    <h5>sessions</h5>
                    { courseStats.sessionids !== undefined &&
                        courseStats.sessionids.slice(0).reverse().slice(0,10).map((sessionid, session_index) =>
                            <li key={sessionid} id={sessionid} onClick={() => handleSessionClicked(sessionid)}>
                                <div>
                                <span style={{ padding: "5px" }}>
                                    { moment(courseStats.session_info[sessionid].date - 1000).format("YYYY-MM-DD") }
                                </span>
                                <span style={{ padding: "5px" }}>
                                    { courseStats.session_info[sessionid].score }
                                </span>
                                <span style={{ padding: "5px" }}>
                                    { sessionid }
                                </span>
                                </div>
                            </li> 
                        )
                    }
                </span>
            </div>

            <br/>

            <div style={{ padding: '20px 150px 10px 0px', margin: '15px' }}>
                {/*
                <hr/>
                <span><hr/>Questions ...</span>
                <br/>
                */}
                <span style={{ }}>
                    <input
                        key="table_filter"
                        style={{ width: '50%' }}
                        onInput={e => setSearchText(e.target.value)}
                        placeholder="search ..."
                    />
                </span>
                <span style={{ margin: '900px' }}>
                    <DataTable
                        noHeader={ true }
                        dense={ true }
                        columns={ tableColumns }
                        data={ tableData }
                        onRowClicked={ handleQuestionRowClicked }
                        customStyles={customStyles}
                        conditionalRowStyles={conditionalRowStyles}
                    />
                </span>
            </div>
		</div>
	);
}

export default CoursePage;
