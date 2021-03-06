import React from 'react';
import { Button } from 'reactstrap';
import { useEffect, useState } from 'react';
import { Link, useLocation, useParams } from "react-router-dom";

import QuestionPage from './Question';
import { InlineQuestion } from './Question';
import { InlineReport } from './Report';

import { postSessionAnswer } from '../Api';

function getCourseIdFromCurrentUrl() {
    // http://localhost:3000/courses/C960_discrete_math_II/quiz
    const thisPath = window.location.pathname;
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
        quizurl = '/api/quiz/' + courseID

        let qCount = query.get('count');
        if (qCount === null || qCount === undefined) {
            qCount = "10";
        };

        const sectionSearchString = query.get('search_section');
        if ( sectionSearchString !== null && sectionSearchString !== undefined && sectionSearchString !== "" ) {
            quizurl += '?' + 'search_section=' + sectionSearchString + '&count=' + qCount;
        } else {
            quizurl += '?' + 'count=' + qCount;
        }

        await fetch(quizurl)
            .then(res => res.json())
            .then((quizData) => {
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
        const newAnswers = [...userAnswers];
        newAnswers[currentQuestionIndex] = e.currentTarget.value;
        setUserAnswers([...newAnswers]);

        const choiceIndex = parseInt(e.currentTarget.id);
        postSessionAnswer(sessionID, courseID, questionIDs[currentQuestionIndex], null, choiceIndex)
    };

    // input box typed in ...
    const handleOnChange = (e) => {
        const newAnswers = [...userAnswers];
        newAnswers[currentQuestionIndex] = e.currentTarget.value;
        setUserAnswers([...newAnswers]);

        postSessionAnswer(sessionID, courseID, questionIDs[currentQuestionIndex], e.target.value, null)
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
                    <div>
                        <span style={{ padding: "5px" }}>
                            <Button color="info" onClick={ goToPreviousQuestion }>prev</Button>
                        </span>
                        <span style={{ padding: "5px" }}>
                            <Button color="success" onClick={ goToNextQuestion }>next</Button>
                        </span>
                        <span style={{ padding: "50px" }}>
                            <Button color="danger" onClick={ handleSubmit }>submit</Button>
                        </span>
                    </div>
                    <hr/>

                    <InlineQuestion
                        key={ questionIDs[currentQuestionIndex] }
                        qindex={ currentQuestionIndex }
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
