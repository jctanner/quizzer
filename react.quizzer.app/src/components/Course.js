import React from 'react';
import { Button } from 'reactstrap';

import { useEffect, useState } from 'react';
import { Link, useHistory, useParams } from "react-router-dom";

import BarChart from 'react-bar-chart';
import DataTable from 'react-data-table-component';

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
            backgroundColor: 'green',
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
            backgroundColor: 'red',
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
    const [tableData, setTableData] = useState([]);
    const [chartOptions, setChartOptions] = useState({});
    const [scoreHistory, setScoreHistory] = useState([]);
    const history = useHistory();

    const chartMargin = {top: 20, right: 20, bottom: 30, left: 40};

	let { courseName } = useParams();
    const tableColumns = [
        {name: 'questionid', selector: 'questionid', compact: true},
        {name: 'average', selector: 'average', compact: true, right: true, sortable: true},
        {name: 'total attempts', selector: 'total', compact: true, right: true, sortable: true},
        {name: 'correct', selector: 'correct', compact: true, right: true},
        {name: 'incorrect', selector: 'incorrect', compact: true, right: true}
    ];

    const handleRowClicked = (row) => {
        console.log(row);
        const rowQuestionId = row.questionid;
        const questionUrl = '/courses/' + courseName + '/questions/' + rowQuestionId;
        //history.push(questionUrl);
        window.location = questionUrl;
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
            // define the chart options
            const chartOpts = {
                animationEnabled: true,
                theme: 'light2',
                title: { text: 'score history' },
                axisX: { title: 'time' },
                axisY: { title: 'score' },
                data: [{
                    type: 'bar',
                    dataPoints: courseStats.score_history
                }]
            }
            setChartOptions(chartOpts);
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

        };

        //fetchQuestionList();
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


    const startQuiz = () => {
        //<Link to={ "/courses/" + courseName + '/quiz' }>start quiz</Link>
        const quizUrl = '/courses/' + courseName + '/quiz';
        history.push(quizUrl)
    };

	return (
		<div>
        	<h2>COURSE: { courseName }</h2>
            <ul>
                <li id='statstotal'>total: { courseStats.total }</li>
                <li id='statsanswered'>answered: { courseStats.answered }</li>
            </ul>
            <BarChart
                margin={ chartMargin }
                ylabel='score'
                width={ 800 }
                height={ 200 }
                data={ scoreHistory }
                />
            <hr/>
            <Button onClick={startQuiz}>start quiz</Button>
            <Button onClick={startQuiz}>start test</Button>
            <hr/>
            <DataTable
                //title="questions"
                noHeader={ true }
                //compact={ true }
                dense={ true }
                //striped={ true } 
                //responsive={ true }
                columns={ tableColumns }
                data={ tableData }
                onRowClicked={ handleRowClicked }
                customStyles={customStyles}
                conditionalRowStyles={conditionalRowStyles}
            />
		</div>
	);
}

export default CoursePage;
