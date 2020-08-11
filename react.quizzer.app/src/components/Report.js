import React from 'react';

import { useEffect, useState } from 'react';
import { Link, useParams } from "react-router-dom";


export const InlineReport = (props) => {
    
    const [ score, setScore ] = useState(0);
    const [ correct, setCorrect ] = useState([]);
    const [ inCorrect, setInCorrect ] = useState([]);
    const [ questionData, setQuestionData ] = useState(null);

    const totalQuestions = props.questionIDs.length;
    useEffect(() => {

        let inCorrectAnswers = [];
        let correctAnswers = [];
        let inCorrectIds = [];
        let correctIds = [];
        for (let i=0; i<props.questionIDs.length; i++) {
            const thisAnswer = props.userAnswers[i];
            console.log('thiAnswer', thisAnswer);

            const thisQuestionID = props.questionIDs[i];
            const questionApiUrl = '/api/courses/' + props.courseName + '/questions/' + thisQuestionID;

            /*
            const fetchQuestionData = async () => {
                //console.log('fetching ' + questionApiUrl)
                const questionData = await fetch(questionApiUrl)
                    .then(res => res.json());
                //console.log(questionData);
                return questionData;
            };
            */
            //const questionData = fetchQuestionData();

            //fetch(questionApiUrl).then(res => res.json()).then(json => setQuestionData(json));
           
            async function checkAnswer(index, qid, answer) {
                const questionApiUrl = '/api/courses/' + props.courseName + '/questions/' + qid;
                fetch(questionApiUrl)
                    .then(res => res.json())
                    .then((data) => {

                        if (answer === data.answer) {
                            console.log(answer, '===', data.answer);
                            //correctIds.push(props.questionIDs[index]);
                            //correctAnswers.push([index, answer, data.answer]);
                            //
                            let tmpCorrect = [...correct];
                            tmpCorrect.push([index, answer, data.answer]);
                            setCorrect([...tmpCorrect]);
                        } else {
                            console.log(answer, '!==', data.answer);
                            //inCorrectIds.push(props.questionIDs[index]);
                            //inCorrectAnswers.push([index, answer, data.answer]);
                            let tmpInCorrect = [...inCorrect];
                            tmpInCorrect.push([index, answer, data.answer]);
                            setInCorrect([...tmpInCorrect]);
                        }

                    })

            }

            checkAnswer(i, thisQuestionID, thisAnswer);
            /*
            console.log(questionData);

            if (thisAnswer === questionData.answer) {
                console.log(thisAnswer, '==', questionData.answer);
                correctIds.push(props.questionIDs[i]);
                correctAnswers.push([i, thisAnswer, questionData.answer]);
            } else {
                console.log(thisAnswer, '!==', questionData.answer);
                inCorrectIds.push(props.questionIDs[i]);
                inCorrectAnswers.push([i, thisAnswer, questionData.answer]);
            }
            */

        }

        //setCorrect([...correctAnswers]);
        //setInCorrect([...inCorrectAnswers]);

        //console.log('correct', correctAnswers);
        //console.log('incorrect', inCorrectAnswers);

        const newScore = (correct.length / totalQuestions.toPrecision(5)) * 100;
        setScore(newScore);
        console.log(score);

        const postOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                sessionid: props.sessiondid,
                coursename: props.courseName,
                score: score,
                total_questions: props.questionIDs.length,
                total_correct: correct.length,
                total_incorrect: inCorrect.lengtha,
                correct: correctIds,
                incorrect: inCorrectIds
            })
        };

        const resultApiUrl = '/api/results';
        fetch(resultApiUrl, postOptions)
            .then(response => response.json());

    }, [])

    return (
        <div>
            <p>REPORT!!!</p>
            <p>{ score }%</p>
            <p>{ correct.length } out of { totalQuestions } correct</p>
            <hr/>
            <h3>Incorrect ...</h3>
            { inCorrect.map((q) => 
                <li>{ props.questionIDs[q[0]] }</li>
            )}
        </div>
    );

}
