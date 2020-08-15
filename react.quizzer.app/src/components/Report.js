import React from 'react';
import { useEffect, useState } from 'react';
import { Link, useParams } from "react-router-dom";

import { getSessionResults } from '../Api';


const InlineQuestionDiv = ({ id, index, courseName, sessionData, question }) => {
    console.log(question);
    let mark = '(u)';
    let color = 'gray';

    const isCorrect = sessionData.correct.includes(question);
    if ( isCorrect ) {
        mark = '(c)';
        color = 'green';
    } else {
        if ( ! sessionData.unanswered.includes(question) ) {
            mark = '(x)';
            color = 'red';
        }
    }

    const handleQuestionClicked = (questionid) => {
        const questionUrl = '/courses/' + sessionData.courseName + '/questions/' + questionid;
        window.location = questionUrl;
    };

    return (
        <li style={{ color: color }} onClick={() => handleQuestionClicked(question)}>
            <div>
            <span>{ index }</span>
            <span style={{ padding: "5px" }}>{ mark }</span>
            <span>{ question }</span>
            </div>
        </li>
    )
}

const InlineQuestionListReport = (props) => {

    const courseName = props.sessionData.coursename;
    const sessionData = props.sessionData;
    const questionIds = props.questionIds;
    console.log(questionIds)

    return (
        <ol>
        { questionIds.map((questionid, index) =>
            <InlineQuestionDiv
                id={ index }
                index={ index }
                courseName={ courseName }
                sessionData={ sessionData }
                question={ questionid }
            />
        )}
        </ol>
    )
}

export const InlineReport = (props) => {
    
    const [ sessionData, setSessionData ] = useState({});
    const [ questionIds, setQuestionIds ] = useState([]);

    const totalQuestions = props.questionIDs.length;
    useEffect(() => {
        console.log('InlineReport useeffect ...');

        async function getResults(sessionid) {
            const newData = await getSessionResults(props.sessionid);
            console.log('newData', newData);
            setSessionData(newData);
            setQuestionIds(newData.sessionQuestionIds);
        }

        getResults(props.sessionid);

    }, [])

    return (
        <div>
            <h5>{ sessionData.courseName } session report</h5>
            <p>SCORE: { sessionData.score }%</p>
            <p>{ sessionData.totalCorrect } out of { sessionData.totalQuestions } correct</p>
            <p>answered { sessionData.totalAnswered } out of { sessionData.totalQuestions } correct</p>
            <hr/>
            <InlineQuestionListReport
                key={ sessionData.sessionid }
                questionIds={ questionIds }
                sessionData={ sessionData }
            />
        </div>
    );

}
