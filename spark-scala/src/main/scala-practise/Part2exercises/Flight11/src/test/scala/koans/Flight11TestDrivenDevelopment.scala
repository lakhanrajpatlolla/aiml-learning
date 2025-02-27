
/* Copyright (C) 2010-2014 Escalate Software, LLC. All rights reserved. */

package koans

import org.scalatest.FunSuite
import org.scalatest.Matchers
import org.scalatest.SeveredStackTraces

/*
  This flight contains 3 different test classes. Please work on them in this order:

  1. Flight11DesignByContract
  2. Flight11TestDrivenDevelopment
  3. Flight11BehaviorDrivenDevelopment
*/
class Flight11TestDrivenDevelopment extends FunSuite with Matchers with SeveredStackTraces {

  // The aim of this exercise is to create a method called stripAllWhitespace that takes
  // a string, and meets the tests that you will write. In the spirit of real test driven
  // development, first write the test you want, check that it fails, and then do the minimum
  // implementation necessary to pass that and all previous tests. We will give you
  // a handy starting point, but for each of the steps below, add the tests first, see that they
  // fail, and then enhance the implementation of the method until it passes.

  // here is the initial implementation and the first test. Note - this is the simplest possible
  // solution that meets the test specification.

  def stripAllWhitespace(s: String) = ""

  // 1. stripAllWhitespace should return empty string when given a single space

  test("stripAllWhitespace should return empty string when given an empty string") {
    stripAllWhitespace("") should be ("")
  }

  // OK - now add the following tests and make them work

  // 2. stripAllWhitespace should return empty string when given a single space
  
  // 3. stripAllWhitespace should return "a" when given " a"

  // 4. stripAllWhitespace should return "hello" when given "    hello    "

  // 5. stripAllWhitespace should return "peterpiperpickedapeckofpickledpeppers" when given
  //    "  peter piper    picked  a peck       of pickled    peppers     "

  // When you have a single implementation of stripAllWhitespace that satisfies all the tests, you are done

}
