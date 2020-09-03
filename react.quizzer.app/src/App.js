import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import CoursePage from './components/Course';
import QuestionPage from './components/Question';
import QuizPage from './components/Quiz';
import SessionPage from './components/Session';
import { Navbar, NavbarBrand, Nav, NavItem, NavLink } from 'react-bootstrap';

import { useEffect, useState } from 'react';

//import ReactDOM from 'react-dom';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";


var mainStyle = {
  background: "#eee",
  padding: "20px",
  margin: "20px"
};

function NotFound() {
    return <div>Not Found</div>
}

// HOME
function Home() {
	return (
		<div><h2>HOME</h2></div>
	)
};

function App() {

    const [ courseList, setCourseList ] = useState([]);

    const fetchCourseList = async () => {
        const newCourseList = await fetch('/api/courses')
            .then(res => res.json())
        console.log(typeof newCourseList);
        setCourseList(newCourseList);
    };

    useEffect(() => {
        fetchCourseList();
    }, [])

    console.log('cl type', typeof courseList);

	return (
		<Router>
        	<div style={{ ...mainStyle }}>
        	    <div style={{ background: '#608f9f', 'border-radius': '5px' }}>
                    <Navbar bg="transparent" expand="lg">
                        <Nav>
                            <NavbarBrand href="/">Quizzer</NavbarBrand>
                            {/*
                            <NavItem><NavLink>test</NavLink></NavItem>
                            <NavItem><NavLink>test2</NavLink></NavItem>
                            */}
                            { courseList.map((courseName) =>
                                <>
                                <div style={{ 'border-left': '1px solid darkgray' }}></div>
                                <NavItem>
                                    <NavLink href={ "/courses/" + courseName } >{ courseName }</NavLink>
                                </NavItem>
                                </>
                            )}
                            <div style={{ 'border-left': '1px solid darkgray' }}></div>
                        </Nav>
                    </Navbar>
                </div>
                {/*
				<ul>
					<li>
						<Link key="home" to="/">Home</Link>
					</li>
            		{courseList.map((courseName) => 
                        <li key={courseName }>
					        <Link to={ "/courses/" + courseName }>{ courseName }</Link>
                        </li>
					)}
				</ul>
                */}
				<Switch>
					<Route exact path="/" component={ Home } />
                    <Route path="/courses/:courseName/quiz" component={ QuizPage }/>
					<Route path="/courses/:courseName/questions/:questionId" component={ QuestionPage } />
					<Route path="/courses/:courseName" component={ CoursePage } />
					<Route path="/sessions/:sessionid" component={ SessionPage } />
                    <Route component={ NotFound } />
				</Switch>
			</div>
		</Router>
	);

}

export default App;
