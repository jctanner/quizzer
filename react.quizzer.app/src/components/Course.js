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

import StatsDiv from './Stats';

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
            /*
            if ( newStats.score_history.length <= 5 ) {
                setScoreHistory(newStats.score_history)
            } else {
                let tmpScoreHistory = [];
                for ( let i = 0; i < 5; i++ ) {
                    tmpScoreHistory.push(newStats.score_history[i]);
                }
                setScoreHistory(tmpScoreHistory);
            }
            */
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

            setTableData(newTableData);
            setAllTableData(newTableData);

        };

        fetchQuestionList();
        fetchCourseStats();

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

    const startFilteredQuiz = () => {
        const quizUrl = '/courses/' + courseName + '/quiz' + '?' + 'search_section=' + searchText;
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

            <StatsDiv
                courseStats={ courseStats }
                scoreHistory={ scoreHistory }
                handleSessionClicked={ handleSessionClicked }
            />
            <br/>

            <div style={{ padding: '20px 150px 10px 10px', margin: '15px' }}>
                <span style={{ padding: '0px 10px 100px 10px' }}>
                    <span>
                    <input
                        key="table_filter"
                        style={{ width: '50%' }}
                        onInput={e => setSearchText(e.target.value)}
                        placeholder="search ..."
                    />
                    </span>
                    <span style={{ padding: '10px 10px 10px 10px' }}>
                    <Button style={{ margin: '10px', padding: '10px 10px 10px 10px' }} onClick={startFilteredQuiz}>quiz</Button>
                    </span>
                </span>
                <span style={{ margin: '900px', padding: '50px' }}>
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
