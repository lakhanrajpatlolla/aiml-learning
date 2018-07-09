package client.misc

import java.io.{File, FileWriter}

import play.api.libs.json.Reads._
import play.api.libs.json._

import scala.collection._
import scala.io.{Codec, Source}

/**
  * Created by lpatlolla on 6/5/18.
  */
case class BulkWorkflowUpdateByParameter() extends Logging {
  def run(args: Array[String]): Unit = {
    val pl = new ProgressLogger(0)
    pl.logStart()

    val cmdArgs = CliParser2("AddParameterToWorkflow", args, BulkWorkflowUpdateByParameter.CommandLineOptions())

    val workflowFiles: List[String] = cmdArgs.workflowDir match {
      case Some(wd) => val files = new FeatureRead(wd, filenamePrefixOpt = Some(cmdArgs.prefix)).fileList
        .map(fl => fl.descr.split("/").toList.takeRight(4).mkString("/")).toList
        logger.info(s"Files from workflow Dir: ${files.size}")
        println(files.head)
        files
      case _ => val mappings = readFile(cmdArgs.bundleMappingsFilePath).as[JsArray]
        val filesFromBM = mappings.value.map { jsO => (jsO.as[JsObject] \ "workflow_path").as[String] }.toList
        logger.info(s"Files from Bundle mappings: ${filesFromBM.size}")
        filesFromBM
    }

    logger.info(s"Total workflow files : ${workflowFiles.size}")

    //val testPath = Seq("workflows/GeometrySimplification/workflow.json")
    addParameterToWorkflowFiles(workflowFiles, cmdArgs.variableName, cmdArgs.variableValue, cmdArgs.parameterKey, cmdArgs.parameterValue, cmdArgs.argsCheckToAdd)

    pl.logEnd()
  }

  private def addParameterToWorkflowFiles(workflowFilePaths: Seq[String], variableName: String, variableValue: String,
    parameterKey: String, parameterValue: String, argsCheckToAddInStep: String, variableToCheck: String = "job_id") = {

    var changedCnt = 0

    val argsTrans = (__ \ 'args).json.update(
      __.read[JsArray].map { case JsArray(o) =>
        changedCnt = changedCnt + 1
        JsArray(o :+ JsString(parameterKey) :+ JsString(parameterValue))
      })

    val workflowStepTransformer = (__ \ 'tasks).json.update(
      __.read[JsArray].map { case JsArray(o) =>
        val x: Seq[JsObject] = o.map { eachStep =>
          val stepObj = eachStep.as[JsObject]
          val args: Option[Seq[String]] = (eachStep.as[JsObject] \ "args").asOpt[JsArray].map(_.value.map(_.as[String]))
          val sparkExists: Boolean = args.map(_.contains(argsCheckToAddInStep)).getOrElse(false)
          if (sparkExists) stepObj.transform(argsTrans).get else stepObj
        }
        JsArray(x)
      }
    )


    val newVariable = Json.arr(Json.obj("name" -> variableName, "value" -> variableValue))
    val varaibleTransformer = (__ \ 'properties \ 'variables).json.update(
      __.read[JsArray].map { o => o ++ newVariable })

    workflowFilePaths.foreach { wf =>
      val workflowJson = readFile(wf).as[JsObject]
      val allVariables = (workflowJson \ "properties" \ "variables").as[JsArray]
      val variableNotExists: Boolean = !allVariables.value.exists { jsV =>
        ((jsV.as[JsObject] \ "name").as[String] == variableName)
      }

      val allTasks = (workflowJson \ "tasks").as[JsArray]

      val validStepToAddParam: Boolean = allTasks.value.exists { jsV =>
        val taskArgs: Array[String] = (jsV.as[JsObject] \ "args").asOpt[JsArray].map(_.value.map(_.as[String])).toArray.flatten
        val sparkExists = taskArgs.contains(argsCheckToAddInStep)
        val jobIdDoesNotExist = !(taskArgs.contains(parameterKey) && taskArgs.contains(parameterValue))
        sparkExists && jobIdDoesNotExist
      }

      val updatedWorkflowOpt: Option[JsObject] = if (validStepToAddParam) {
        val updatedWorkflow: JsObject = if (variableNotExists) workflowJson.transform(varaibleTransformer).getOrElse(workflowJson) else workflowJson
        val updatedTask = updatedWorkflow.transform(workflowStepTransformer).getOrElse(updatedWorkflow)

        validateVariable(updatedTask, variableName)
        validateParametersInTask(updatedTask, argsCheckToAddInStep, parameterKey, parameterValue)

        Some(updatedTask)
      } else None

      updatedWorkflowOpt.map(writeToFile(_, wf, fileIndex = changedCnt))

    }

    logger.info(s"Total Changed workflow count : $changedCnt")

  }

  def validateVariable(updatedWorkflow: JsObject, variableName: String) = {
    val name: String = (updatedWorkflow \ "name").as[String]
    val allVariables = (updatedWorkflow \ "properties" \ "variables").as[JsArray]
    val requiredVariable: Seq[JsValue] = allVariables.value.filter { jsV =>
      ((jsV.as[JsObject] \ "name").as[String] == variableName)
    }
    assert(requiredVariable.size <=1 , s"Variable: ${variableName}, found more than one in workflow - $name")
    requiredVariable.size == 1
  }


  def validateParametersInTask(updatedWorkflow: JsObject, argsCheckToAddInStep: String, parameterKey: String, parameterValue: String): Boolean = {

    val name: String = (updatedWorkflow \ "name").as[String]
    val paramList = List(parameterKey,parameterValue)

    val allTasks = (updatedWorkflow \ "tasks").as[JsArray]
    val validChangedStep = allTasks.value.find { jsV =>
      val taskArgs: Array[String] = (jsV.as[JsObject] \ "args").asOpt[JsArray].map(_.value.map(_.as[String])).toArray.flatten
      val sparkExists = taskArgs.contains(argsCheckToAddInStep)
      if (sparkExists)  taskArgs.filter(paramList.contains).size == paramList.size else true
    }
    assert(validChangedStep.isDefined, s"workflow task may have introduced duplicate parameters: $parameterKey, " +
      s"value: $parameterValue in step: $argsCheckToAddInStep in workflow name: $name")
    validChangedStep.isDefined

  }

  def writeToFile(updated: JsObject, outputPath: String, fileIndex: Int) = {
    val file = new File(outputPath)
    if (!file.getParentFile.exists()) {
      file.getParentFile.mkdirs()
    }
    val wrFile = new FileWriter(file)
    logger.info(s"Writing file $fileIndex : ${file.getAbsolutePath}")

    Json.prettyPrint(updated).map { line =>
      wrFile.write(line)
    }
    wrFile.close()
  }

  def readFile(path: String) = {
    Json.parse(Source.fromFile(path)(Codec.UTF8).getLines().mkString)
  }
}

object BulkWorkflowUpdateByParameter extends App {
  BulkWorkflowUpdateByParameter().run(args)

  case class CommandLineOptions(
    @helpText(msg = "Auth") @shortName(name = 'a') auth: String = scala.util.Properties.envOrElse("AUTH_TOKEN", "AUTH_NOT_DEFINED"),
    @helpText(msg = "Bundle Mappings File Path") @shortName(name = 'f') bundleMappingsFilePath: String = "workflows/BundleMappings.json",
    @helpText(msg = "workflow directory Path") @shortName(name = 'f') workflowDir: Option[String] = None,//Some("workflows"),
    @helpText(msg = "workflow name prefix") @shortName(name = '3') prefix: String = "workflow",
    @helpText(msg = "variable check") @shortName(name = 'e') variableName: String = "job_id",
    @helpText(msg = "variable check") @shortName(name = 'e') variableValue: String = "TBD",
    @helpText(msg = "workflow step to add") @shortName(name = 'e') argsCheckToAdd: String = "run_spark_job",
    @helpText(msg = "variable check") @shortName(name = 'e') parameterKey: String = "--jobId",
    @helpText(msg = "variable check") @shortName(name = 'e') parameterValue: String = "${job_id}"
  )

}
