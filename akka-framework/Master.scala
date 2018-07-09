package client.akkaPractise


import akka.actor._
import akka.routing.RoundRobinPool
import scala.concurrent.duration._

/**
  * Created by lpatlolla on 5/7/18.
  */
class Master(nrOfWorkers: Int, nrOfMessages: Int, nrOfElements: Int, listener: ActorRef)
  extends Actor {

  var pi: Double = _
  var nrOfResults: Int = _
  val start: Long = System.currentTimeMillis

  val workerRouter = context.actorOf(
    Props[Worker].withRouter(RoundRobinPool(nrOfWorkers)), name = "workerRouter")

  def receive = {
    case Calculate ⇒
      for (i ← 0 until nrOfMessages) workerRouter ! Work(i * nrOfElements, nrOfElements)
    case Result(value) ⇒
      pi += value
      nrOfResults += 1
      if (nrOfResults == nrOfMessages) {
        // Send the result to the listener
        listener ! PiApproximation(pi, duration = (System.currentTimeMillis - start).millis)
        // Stops this actor and all its supervised children
        context.stop(self)
      }
  }

}
