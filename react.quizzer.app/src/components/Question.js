import React from 'react';

import { useEffect, useState } from 'react';
import { Link, useParams } from "react-router-dom";

import { postSessionAnswer } from '../Api';


function QuestionDiv(props) {

    const courseName = props.courseName;
    const questionID = props.questionID;
    let questionData = props.questionData;
    const handleSelect = props.handleSelect;
    const handleOnChange = props.handleOnChange;
    let answerHidden = props.answerHidden;
    const toggleAnswer = props.toggleAnswer;
    let userChoice = props.userChoice;
    const showPreviousNext = props.showPreviousNext;
    let showImages = props.showImages;
    const toggleImages = props.toggleImages;

    console.log('--------------------------------------------')
    console.log(questionData);
    console.log('--------------------------------------------')

    useEffect(() => {
        console.log('#######################################');
        console.log('props.currentSelection', props.currentSelection);
        console.log('props.userSelection', props.userSelection);
        console.log('#######################################');
    });

    return (
        <div style={{ 'margin-top': '20px'}}>
            <li><strong>{ questionID }</strong> { questionData.section }</li>
            <hr/>
            { ( showImages ) && <button onClick={ toggleImages }>html</button> }
            { ( !showImages ) && <button onClick={ toggleImages }>images</button> }
            <hr/>

            { (!showImages) && <div dangerouslySetInnerHTML={ { __html: questionData.instructions } }></div> }
            { (showImages && questionData.images) && <img src={ '/images/' + courseName + '/' + questionData.images.instructions }/> }

            { (showImages) && <br/> }
            { (showImages) && <br/> }

            { (!showImages) && <div dangerouslySetInnerHTML={ { __html: questionData.question } }></div> }
            { (showImages && questionData.images) && <img src={ '/images/' + courseName + '/' + questionData.images.question }/> }

            <hr/>
            { (questionData.input_type === "fieldset") && 
                <div>
                <h3>choices</h3>
                <form>
                    <fieldset>
                    { questionData.choices.map((choice, index) => (
                        <div>
                            <input 
                                onChange={ props.handleSelect }
                                checked={ choice === props.currentSelection || choice === props.userSelection }
                                type="radio"
                                value={ choice }
                                key={ index }
                                id={ index }
                            />
                            { (!showImages && choice.includes('<div')) && <div dangerouslySetInnerHTML={ { __html: choice } }></div> } 
                            { (!showImages && !choice.includes('<div')) && choice } 
                            { (showImages && questionData.images && questionData.images.choices) &&
                                <img src={ '/images/' + courseName + '/' + questionData.images.choices[index] }/>
                            }

                        </div>
                    ))}
                    </fieldset>
                </form>
                </div>
            }
            { (questionData.input_type === "input" || questionData.input_type !== "fieldset") && 
                <form>
                    <input
                        key={ props.questionID }
                        onChange={ props.handleOnChange }
                        type="text"
                        value={ props.currentSelection }
                    />
                </form>
            }
            <hr/>
            { (answerHidden === true) &&
                <button onClick={ toggleAnswer }>show answer</button>
            }
            { (answerHidden !== true) &&
                <button onClick={ toggleAnswer }>hide answer</button>
            }

            { (answerHidden === false && !showImages) && <div><h3>answer</h3><div dangerouslySetInnerHTML={ { __html: questionData.answer } }></div><h3>explanation</h3><div dangerouslySetInnerHTML={ { __html: questionData.explanation } }></div></div> }
            { (answerHidden === false && showImages && questionData.images) && <div>
                <img src={ '/images/' + courseName + '/' + questionData.images.explanation }/>
                </div> }

            <hr/>
            { (showPreviousNext && questionData.previous !== null) && <button><a href={ questionData.previous }>previous</a></button> }
            { (showPreviousNext &&  questionData.next !== null) && <button><a href={ questionData.next }>next</a></button> }

        </div>
    );
};

// A SINGLE QUESTION
function QuestionPage() {
   
    console.log('question page ...');

    const [showImages, setShowImages] = useState(true);
    const [userChoice, setUserChoice] = useState(null);
    const [answerHidden, setAnswerHidden] = useState(true);
    const [questionData, setQuestionData] = useState([]);
    let { courseName, questionId } = useParams();
    const questionApiUrl = '/api/courses/' + courseName + '/questions/' + questionId;
    console.log(questionApiUrl)

    const handleSelect = (e) => {
        console.log(e);
        console.log('selected Zvalue', e.currentTarget.value);
        setUserChoice(e.currentTarget.value);
    };

    const handleOnChange = (e) => {
        console.log(e.target.value);
        setUserChoice(e.target.value);
    };

    const toggleAnswer = (e) => {
        if ( answerHidden === true ) {
            setAnswerHidden(false)
        } else {
            setAnswerHidden(true);
        }
    };

    const toggleImages = (e) => {
        if ( showImages === true ) {
            setShowImages(false)
        } else {
            setShowImages(true);
        }
    };

    useEffect(() => {

        const fetchQuestionData = async () => {
            console.log('fetching ' + questionApiUrl)
            const newQuestionData = await fetch(questionApiUrl)
                .then(res => res.json());
            console.log(newQuestionData);
            setQuestionData(newQuestionData);
        };

        fetchQuestionData();

        return () => {
            console.log('cleanup');
        };
    }, [questionApiUrl]);

    return (
        <QuestionDiv
            key={ 1 }
            courseName={ courseName }
            questionID={ questionId }
            questionData={ questionData }
            handleOnChange={ handleOnChange }
            answerHidden={ answerHidden }
            toggleAnswer={ toggleAnswer }
            userChoice={ userChoice }
            showPreviousNext={ true }
            showImages={ showImages }
            toggleImages={ toggleImages }
        />
    );
};


export const InlineQuestion = (props) => {

    //const [userChoice, setUserChoice] = useState(null);
    const [answerHidden, setAnswerHidden] = useState(true);
    const [questionData, setQuestionData] = useState([]);
    const [showImages, setShowImages] = useState(true);

    const courseName = props.courseName;
    const questionID = props.questionID;
    const questionApiUrl = '/api/courses/' + courseName + '/questions/' + questionID;
    console.log(questionApiUrl)

    const toggleAnswer = (e) => {
        if ( answerHidden === true ) {
            setAnswerHidden(false)
        } else {
            setAnswerHidden(true);
        }
    };

    const toggleImages = (e) => {
        if ( showImages === true ) {
            setShowImages(false)
        } else {
            setShowImages(true);
        }
    };

    /*
    const handleSelect = (e) => {
        console.log(e);
        console.log('selected Zvalue', e.currentTarget.value);
        setUserChoice(e.currentTarget.value);
    };

    const handleOnChange = (e) => {
        props.console.log(e.target.value);
        props.setUserChoice(e.target.value);
    };
    */

    useEffect(() => {

        const fetchQuestionData = async () => {
            const newQuestionData = await fetch(questionApiUrl)
                .then(res => res.json());
            setQuestionData(newQuestionData);
            props.setCurrentQuestionData(newQuestionData);
        };

        fetchQuestionData();

        return () => {
            console.log('cleanup');
        };
    }, [questionApiUrl]);

    useEffect(() => {
        console.log('###################################### 1');
        console.log('props.currentSelection', props.currentSelection);
        console.log('props.userSelection', props.userSelection);
        console.log('###################################### 1');
    });

    return (
        <QuestionDiv
            key={ questionID }
            courseName={ courseName }
            quesitonID={ questionID }
            questionData={ questionData }
            handleOnChange={ props.handleOnChange }
            handleSelect={ props.handleSelect }
            answerHidden={ answerHidden }
            toggleAnswer={ toggleAnswer }
            userChoice={ props.userChoice }
            userSelection={ props.userSelection }
            currentSelection={ props.currentSelection }
            showPreviousNext={ false }
            showImages={ showImages }
            toggleImages={ toggleImages }
        />
    );
};

export default QuestionPage;
