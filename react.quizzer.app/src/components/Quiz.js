import React from 'react';
import { useEffect, useState } from 'react';
import { Link, useLocation, useParams } from "react-router-dom";

import QuestionPage from './Question';
import { InlineQuestion } from './Question';
import { InlineReport } from './Report';

import { postSessionAnswer } from '../Api';

function getCourseIdFromCurrentUrl() {
    // http://localhost:3000/courses/C960_discrete_math_II/quiz
    const thisPath = window.location.pathname;
    console.log('thisPath', thisPath);
    const thisPathParts = thisPath.split('/');
    const totalParts = thisPathParts.length;
    return thisPathParts[totalParts - 2];
};


function useQuery() {
    return new URLSearchParams(useLocation().search);
}

function QuizPage({ multiplechoice }) {

    const [ courseID, setCourseID ] = useState(null);
    const [ sessionID, setSessionID ] = useState(null);
    const [ questionIDs, setQuestionIDs ] = useState([]);
    const [ userAnswers, setUserAnswers ] = useState([].fill(null, 10));
    const [ timeStarted, setTimeStarted ] = useState(null);
    const [ timeFinished, setTimeFinished ] = useState(null);
    const [ currentQuestionIndex, setCurrentQuestionIndex ] = useState(0);
    const [ currentQuestionData, setCurrentQuestionData ] = useState(null);
    const [ currentChoiceIndex, setCurrentChoiceIndex ] = useState(null);
    const [ isMultipleChoice, setIsMultipleChoice ] = useState(true);

    if ( courseID === null) {
        setCourseID(getCourseIdFromCurrentUrl());
    }

    //setIsMultipleChoice(getMutipleChoiceUrlQuery());
    let query = useQuery();
    if (query.get("multiplechoice") !== null) {
        setIsMultipleChoice(true);
    }

    /*
    fetch(questionApiUrl)
                    .then(res => res.json())
                    .then((data) => {
    */

    const fetchQuiz = async () => {

        let quizurl = null;
        if (isMultipleChoice) { 
            quizurl = '/api/quiz/' + courseID + '?muliplechoice=1'
        } else {
            quizurl = '/api/quiz/' + courseID
        }
        console.log('quizurl', quizurl)
        await fetch(quizurl)
            .then(res => res.json())
            .then((quizData) => {
                console.log('quizData', quizData);
                setTimeStarted(quizData.started);
                setTimeFinished(quizData.finished);
                setSessionID(quizData.sessionid);
                setQuestionIDs(quizData.questions);
            })
    };

    const handleSubmit = (e) => { 
        const d = new Date();
        const now = d.getTime();
        setTimeFinished(now);
    }

    const goToNextQuestion = (e) => { 
        if (currentQuestionIndex < (questionIDs.length - 1)) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
        }
    };

    const goToPreviousQuestion = (e) => { 
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(currentQuestionIndex - 1);
        }
    };

    // radio box selected ...
    const handleSelect = (e) => {
        console.log('e', e);
        console.log('e.currentTargte', e.currentTarget);
        console.log('selected value', e.currentTarget.value);
        //setUserChoice(e.currentTarget.value);
        const newAnswers = [...userAnswers];
        newAnswers[currentQuestionIndex] = e.currentTarget.value;
        setUserAnswers([...newAnswers]);

        console.log('currentQuestionData', currentQuestionData);
        const choiceIndex = parseInt(e.currentTarget.id);
        postSessionAnswer(sessionID, courseID, questionIDs[currentQuestionIndex], null, choiceIndex)
    };

    // input box typed in ...
    const handleOnChange = (e) => {
        console.log(e.target.value);
        //setUserChoice(e.target.value);
        const newAnswers = [...userAnswers];
        newAnswers[currentQuestionIndex] = e.currentTarget.value;
        setUserAnswers([...newAnswers]);
    };

    useEffect(() => {
        if ( questionIDs.length === 0 ) {
            fetchQuiz();
        };
    }, [])

	return (
        <div>
            <h2>A QUIZ!</h2>
            <div>
                course: <strong>{courseID}</strong><br/>
                session: <strong>{sessionID}</strong><br/>
                started: <strong>{ timeStarted }</strong><br/>
                finished: <strong>{ timeFinished }</strong><br/>
                question: <strong>{ currentQuestionIndex + 1} of { questionIDs.length }</strong><br/>
            </div>
            <hr/>
            { ( timeFinished === null ) &&

                <div>
                    <button onClick={ goToPreviousQuestion }>prev</button>
                    <button onClick={ goToNextQuestion }>next</button>
                    <button onClick={ handleSubmit }>submit</button>
                    <hr/>

                    <InlineQuestion
                        key={ questionIDs[currentQuestionIndex] }
                        sessionid={ sessionID }
                        courseName={ courseID }
                        questionID={ questionIDs[currentQuestionIndex] }
                        currentSelection={ userAnswers[currentQuestionIndex] }
                        handleSelect={ handleSelect }
                        handleOnChange={ handleOnChange }
                        setCurrentQuestionData={ setCurrentQuestionData }
                    />
                </div>
            }
            { ( timeFinished !== null ) &&
                <InlineReport
                    sessionid={ sessionID }
                    courseName={ courseID }
                    questionIDs={ questionIDs }
                    userAnswers={ userAnswers }
                />
            }

        </div>
	);

}

export default QuizPage;
