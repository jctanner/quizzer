import React from 'react';
import { useHistory } from "react-router-dom";

import { useEffect, useState } from 'react';
import { Link, useParams } from "react-router-dom";
import { Button } from 'reactstrap';

import { postSessionAnswer } from '../Api';


function QuestionInstructions(props) {

    const courseName = props.courseName;
    const questionData = props.questionData;
    const showImages = props.showImages;
   
    let imgfile = null; 
    if (questionData.images && questionData.images.instructions !== undefined) {
        imgfile = '/images/' + courseName + '/' + questionData.images.instructions;
    }

    return (
        <>
            { (showImages && imgfile) && (
                <>
                    <img src={ imgfile }/>
                    <br/>
                    <br/>
                </>
            )}
            { ((imgfile === null || !showImages) && questionData.instructions) && (
                <div dangerouslySetInnerHTML={ { __html: questionData.instructions } }></div> 
            )}
        </>
    )
}

function QuestionChoices(props) {

    const courseName = props.courseName;
    const questionData = props.questionData;
    const showImages = props.showImages;
    const userSelection = props.userSelection;
    const currentSelection = props.currentSelection;
    const handleSelect = props.handleSelect;

    const getChoiceImageUrl = (index) => {
        let imgurl = null;
        if (questionData.images && questionData.images.choices && questionData.images.choices[index]) {
            imgurl = '/images/' + courseName + '/' + questionData.images.choices[index];
        }
        return imgurl;
    }

    const getDisplayTypeForChoice = (index) => {
        let dtype = null;
        if (questionData.images.choices[index] !== null && questionData.images.choices[index] !== undefined) {
            dtype = 'img';
        } 
        if (!showImages || dtype === null) {
            if (questionData.choices[index].includes('<div')) {
                dtype = 'html'
            } else {
                dtype = 'text';    
            }
        }
        return dtype;
    }

    const hasChoiceImages = getChoiceImageUrl(0);

    return (
        <>
            <h3>choices</h3>
            <form>
                <fieldset>
                { questionData.choices.map((choice, index) => (
                    <>
                        <input 
                            onChange={ handleSelect }
                            checked={ choice === currentSelection || choice === userSelection }
                            type="radio"
                            value={ choice }
                            key={ index }
                            id={ index }
                        />
                        { (getDisplayTypeForChoice(index) === 'img') && (
                            <>
                            <img src={ getChoiceImageUrl(index) }/>
                            <br/>
                            </>
                        )}
                        { (getDisplayTypeForChoice(index) === 'html') && (
                             <div dangerouslySetInnerHTML={ { __html: choice } } />
                        )}
                        { (getDisplayTypeForChoice(index) === 'text') && (
                            <>{ choice }<br/></>
                        )}
                    </>
                ))}
                </fieldset>
            </form>
        </>
    )
}


function QuestionAnswer(props) {
    const showImages = props.showImages;
    const courseName = props.courseName;
    const questionData = props.questionData;

    let explanationImg = null; 
    if (questionData.images && questionData.images.explanation !== undefined && questionData.images.explanation !== null) {
        explanationImg = '/images/' + courseName + '/' + questionData.images.explanation;
    }

    const getDisplayTypeForExplanation = () => {
        let dtype = null;
        if (showImages && questionData.images.explanation !== null && questionData.images.explanation !== undefined) {
            dtype = 'img';
        } 
        if (dtype === null && questionData.explanation !== null && questionData.explanation !== undefined) {
            if (questionData.explanation.includes('<div')) {
                dtype = 'html'
            } else {
                dtype = 'text';    
            }
        }
        return dtype;
    }

    return (
        <>
            <h3>answer</h3>
            <div dangerouslySetInnerHTML={ { __html: questionData.answer } }></div>

            {( getDisplayTypeForExplanation() == 'img') && (
                <>
                <h3>explanation</h3>
                <img src={ explanationImg }/>
                </>
            )}
            {( getDisplayTypeForExplanation() == 'html') && (
                <>
                <h3>explanation</h3>
                <div dangerouslySetInnerHTML={ { __html: questionData.explanation } } />
                </>
            )}
            {( getDisplayTypeForExplanation() == 'text') && (
                <>
                <h3>explanation</h3>
                <div>{questionData.explanation}</div>
                </>
            )}
        </>
    )
}

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

    const showCheckButton = props.showCheckButton;
    const questionApiUrl = '/api/courses/' + courseName + '/questions/' + questionID;

    // use these to highlight correct/incorrect answers
    const isChecked = props.isChecked;
    const isCorrect = props.isCorrect;

    let inputStyle = {};
    if (isChecked) {
        if (isCorrect) {
            inputStyle = {color: 'green'}
        } else {
            inputStyle = {color: 'red'}
        }
    }

    return (
        <div style={{ marginTop: '20px'}}>
            <li><strong>{ questionID }</strong> { questionData.section }</li>
            <li>{ questionData.filename }</li>
            <hr/>
            { ( showImages ) && <Button onClick={ toggleImages }>use html</Button> }
            { ( !showImages ) && <Button onClick={ toggleImages }>use images</Button> }

            { (showCheckButton) && (
                <Button style={{ marginLeft: '10px' }} onClick={ props.handleCheck }>check</Button>
            )}

            { (answerHidden === true) &&
                <Button style={{ marginLeft: '10px' }} onClick={ toggleAnswer }>show answer</Button>
            }
            { (answerHidden !== true) &&
                <Button style={{ marginLeft: '10px' }} onClick={ toggleAnswer }>hide answer</Button>
            }

            { (showPreviousNext && questionData.previous !== null) && (
                <Button style={{ marginLeft: '400px' }} onClick={ props.handlePrevious }>
                    {/*<a href={ questionData.previous }>previous</a> */}
                    Last
                </Button> 
            )}
            { (showPreviousNext &&  questionData.next !== null) && (
                <Button style={{ marginLeft: '10px' }} onClick={ props.handleNext }>
                    {/*<a href={ questionData.next }>next</a>*/}
                    Next 
                </Button> 
            )}

            <hr/>

            <QuestionInstructions
                key={ questionID }
                courseName={ courseName }
                questionData={ questionData }
                showImages={ showImages }
            />

            { (!showImages) && <div dangerouslySetInnerHTML={ { __html: questionData.question } }></div> }
            { (showImages && questionData.images) && <img src={ '/images/' + courseName + '/' + questionData.images.question }/> }

            <hr/>
            { (questionData.input_type === "fieldset") && 
                <QuestionChoices
                    courseName={ courseName }
                    questionData={ questionData }
                    showImages={ showImages }
                    handleSelect={ props.handleSelect }
                    currentSelection={ props.currentSelection }
                    userSelection={ props.userSelection }
                />
            }
            { (questionData.input_type === "input" || questionData.input_type !== "fieldset") &&  (
                <form>
                    <input
                        style={ inputStyle }
                        key={ props.questionID }
                        onChange={ props.handleOnChange }
                        type="text"
                        value={ props.currentSelection }
                    />
                </form>
            )}
            {( isChecked && isCorrect ) && (<div style={{ color: 'green' }}>Correct!</div>)}
            {( isChecked && !isCorrect ) && (<div style={{ color: 'red' }}>incorrect.</div>)}

            { (!answerHidden) && (
                <>
                <hr/>
                <QuestionAnswer
                    showImages={showImages}
                    courseName={courseName}
                    questionData={questionData}
                />
                </>
            )}

        </div>
    );
};

// A SINGLE QUESTION (NOT PART OF A QUIZ VIEW)
function QuestionPage() {

    const [isChecked, setIsChecked] = useState(false);
    const [isCorrect, setIsCorrect] = useState(false);

    const [showImages, setShowImages] = useState(true);
    const [userChoice, setUserChoice] = useState(null);
    const [answerHidden, setAnswerHidden] = useState(true);
    const [questionData, setQuestionData] = useState([]);
    let { courseName, questionId } = useParams();
    const questionApiUrl = '/api/courses/' + courseName + '/questions/' + questionId;
    const history = useHistory();

    const handlePrevious = (e) => {
        setIsChecked(false);
        setIsCorrect(false)
        history.push(questionData.previous);
    }
    const handleNext = (e) => {
        setIsChecked(false);
        setIsCorrect(false)
        history.push(questionData.next);
    }

    const handleCheck = (e) => {
        setIsChecked(true);
        console.log('checking:', e);
        console.log('checking userChoice:', userChoice);

        if (userChoice == questionData.answer) {
            setIsCorrect(true)
        } else {
            setIsCorrect(false)
        }

        postSessionAnswer(null, courseName, questionId, userChoice, null);
    };

    const handleSelect = (e) => {
        //console.log(e);
        //console.log('selected Zvalue', e.currentTarget.value);
        setUserChoice(e.currentTarget.value);
    };

    const handleOnChange = (e) => {
        //console.log(e.target.value);
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
            //console.log('fetching ' + questionApiUrl)
            const newQuestionData = await fetch(questionApiUrl)
                .then(res => res.json());
            //console.log(newQuestionData);
            setQuestionData(newQuestionData);
            if (!('images' in newQuestionData)) {
                setShowImages(false);
            };
        };

        fetchQuestionData();

        return () => {
            //console.log('cleanup');
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
            showCheckButton={ true }
            isChecked={ isChecked }
            isCorrect={ isCorrect }
            handleCheck={ handleCheck }
            handlePrevious={ handlePrevious }
            handleNext={ handleNext }
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
    //console.log(questionApiUrl)

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
            const newQuestionData = await fetch(questionApiUrl)
                .then(res => res.json());
            setQuestionData(newQuestionData);
            props.setCurrentQuestionData(newQuestionData);
            if (!('images' in newQuestionData)) {
                setShowImages(false);
            };
        };

        fetchQuestionData();

        return () => {
            //console.log('cleanup');
        };
    }, [questionApiUrl]);

    useEffect(() => {
        /*
        console.log('###################################### 1');
        console.log('props.currentSelection', props.currentSelection);
        console.log('props.userSelection', props.userSelection);
        console.log('###################################### 1');
        */
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
            showCheckButton={ false }
        />
    );
};

export default QuestionPage;
