import React from 'react';
import { useEffect, useState } from 'react';
import { Link, useParams } from "react-router-dom";

import { getSessionResults } from '../Api';


const InlineQuestionDiv = ({ id, sessionData, question }) => {
    console.log(question);
    const isCorrect = sessionData.correct.includes(question);
    let mark = '(!)'
    if ( isCorrect ) {
        mark = '(c)'
    } else {
        if ( ! sessionData.unanswered.includes(question) ) {
            mark = '(x)'
        }
    }

    return (
        <li>
            <div>{ mark }</div>
            <div>{ question }</div>
        </li>
    )
}

const InlineQuestionListReport = (props) => {

    const sessionData = props.sessionData;
    const questionIds = props.questionIds;
    console.log(questionIds)

    return (
        <ol>
        { questionIds.map((questionid, index) =>
            <InlineQuestionDiv
                id={ index }
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
            <p>REPORT!!!</p>
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
