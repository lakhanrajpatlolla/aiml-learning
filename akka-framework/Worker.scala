package client.akkaPractise

import akka.actor._
import scala.concurrent.duration.Duration

/**
  * Created by lpatlolla on 5/7/18.
  */
class Worker extends Actor {

  def calculatePiFor(start: Int, nrOfElements: Int): Double = {
    var acc = 0.0
    for (i ← start until (start + nrOfElements))
      acc += 4.0 * (1 - (i % 2) * 2) / (2 * i + 1)
    acc
  }

  def receive = {
    case Work(start, nrOfElements) ⇒
      sender ! Result(calculatePiFor(start, nrOfElements)) // perform the work
  }
}


sealed trait PiMessage
case object Calculate extends PiMessage
case class Work(start: Int, nrOfElements: Int) extends PiMessage
case class Result(value: Double) extends PiMessage
case class PiApproximation(pi: Double, duration: Duration)
