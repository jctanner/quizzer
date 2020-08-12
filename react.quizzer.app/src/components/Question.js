import React from 'react';

import { useEffect, useState } from 'react';
import { Link, useParams } from "react-router-dom";

import { postSessionAnswer } from '../Api';


// A SINGLE QUESTION
function QuestionPage() {
   
    console.log('question page ...');

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
        <div>
            { questionData.section }
            <hr/>
           
            { (questionData.instructions) && 
                <div>
                    <h4>instructions</h4>
                    <div dangerouslySetInnerHTML={ { __html: questionData.instructions } }></div>
                </div>
            }

            <h3>question</h3>
            <div dangerouslySetInnerHTML={ { __html: questionData.question } }></div>
            <hr/>
            { (questionData.input_type === "fieldset") && 
                <div>
                <h3>choices</h3>
                <form>
                    <fieldset>
                    { questionData.choices.map((choice, index) => (
                        <div>
                            <input 
                                onChange={ handleOnChange }
                                checked={ choice === userChoice }
                                type="radio"
                                value={ choice }
                                key={ index }
                            />
                            { choice.includes('<div')
                                ? <div dangerouslySetInnerHTML={ { __html: choice } }></div>
                                : choice
                            }
                            {/*{ ' ' + choice }*/}
                        </div>
                    ))}
                    </fieldset>
                </form>
                </div>
            }
            { (questionData.input_type === "input" || questionData.input_type !== "fieldset") && 
                <form>
                    <input
                        onChange={ handleOnChange }
                        type="text"
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
            { (answerHidden === false) &&
                <div>
                <h3>answer</h3>
                <div dangerouslySetInnerHTML={ { __html: questionData.answer } }></div>
                <h3>explanation</h3>
                <div dangerouslySetInnerHTML={ { __html: questionData.explanation } }></div>
                </div>
            }
            <hr/>
            { (questionData.previous !== null) && 
                <button>
                    <a href={ questionData.previous }>previous</a>
                </button>
            }
            { (questionData.next !== null) && 
                <button>
                    <a href={ questionData.next }>next</a>
                </button>
            }

        </div>
    );


}

export const InlineQuestion = (props) => {

    const [userChoice, setUserChoice] = useState(null);
    const [answerHidden, setAnswerHidden] = useState(true);
    const [questionData, setQuestionData] = useState([]);

    const questionApiUrl = '/api/courses/' + props.courseName + '/questions/' + props.questionID;

    console.log(questionApiUrl)

    /*
    const handleSelect = (e) => {

        console.log('handleselect.post...');
        //postSessionAnswer(props.sessionid, props.courseName, props.questionID, e.currentTarget.value, null)

        console.log(e.target.value);
        console.log('selected Xvalue', e.currentTarget.value);
        setUserChoice(e.currentTarget.value);

        //console.log('handleselect.post...');
        //postSessionAnswer(props.sessionid, props.courseName, props.questionID, e.currentTarget.value, null)
    };

    const handleOnChange = (e) => {
        console.log(e.target.value);
        console.log('typed value', e.currentTarget.value);
        setUserChoice(e.target.value);
        console.log('handleOnChange.post...');
        postSessionAnswer(props.sessionid, props.courseName, props.questionID, e.currentTarget.value, null)
    };
    */

    const toggleAnswer = (e) => {
        if ( answerHidden === true ) {
            setAnswerHidden(false)
        } else {
            setAnswerHidden(true);
        }
    };

    useEffect(() => {

        const fetchQuestionData = async () => {
            //console.log('fetching ' + questionApiUrl)
            const newQuestionData = await fetch(questionApiUrl)
                .then(res => res.json());
            //console.log(newQuestionData);
            setQuestionData(newQuestionData);
            props.setCurrentQuestionData(newQuestionData);
        };

        fetchQuestionData();

        return () => {
            console.log('cleanup');
        };
    }, [questionApiUrl]);

    return (
        <div>
            { questionData.section }
            <hr/>
           
            { (questionData.instructions) && 
                <div>
                    <h4>instructions</h4>
                    <div dangerouslySetInnerHTML={ { __html: questionData.instructions } }></div>
                </div>
            }

            <h3>question</h3>
            <div dangerouslySetInnerHTML={ { __html: questionData.question } }></div>
            <hr/>
            { (questionData.input_type === "fieldset") && 
                <div>
                <h3>choices</h3>
                <form>
                    <fieldset>
                    { questionData.choices.map((choice, index) => (
                        <div key={ index }>
                            <input 
                                onChange={ props.handleSelect }
                                checked={ choice === props.currentSelection }
                                type="radio"
                                value={ choice }
                                key={ index }
                                id={ index }
                            />
                            { choice.includes('<div')
                                ? <div dangerouslySetInnerHTML={ { __html: choice } }></div>
                                : choice
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
                        value={props.currentSelection}
                    />
                </form>
            }
            <hr/>
            { (answerHidden === true) &&
                <button key={ props.questionID } onClick={ toggleAnswer }>show answer</button>
            }
            { (answerHidden !== true) &&
                <button key={ props.questionID } onClick={ toggleAnswer }>hide answer</button>
            }
            { (answerHidden === false) &&
                <div>
                <h3>answer</h3>
                <div dangerouslySetInnerHTML={ { __html: questionData.answer } }></div>
                <h3>explanation</h3>
                <div dangerouslySetInnerHTML={ { __html: questionData.explanation } }></div>
                </div>
            }

        </div>
    );


}

export default QuestionPage;
