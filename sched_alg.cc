/* Aus argos-research/genode-AdmCtrl/src/sched_controller */

/*
 * \brief
 * \author Paul Nieleck
 * \date   2016/09/22
 */

#include <base/printf.h>
#include "rq_task/rq_task.h"
#include "sched_controller/sched_alg.h"
#include <math.h>

namespace Sched_controller
{
	bool Sched_alg::_compute_repsonse_time(Rq_task::Rq_task *new_task, int num_elements, Rq_task::Rq_task *check_task)
	{
		Rq_task::Rq_task *_curr_task;
		_response_time_old = check_task->wcet;
		while (true)
		{
			_curr_task = _first_task;
			_response_time = check_task->wcet;
			for (int i=0; i<num_elements; ++i)
			{
				_response_time += ceil((double)_response_time_old / (double)_curr_task->inter_arrival) * _curr_task->wcet;
				_curr_task++;
			}

			//If check_task is another task then new task we have to add the new task here
			if (new_task != check_task)
			{
				_response_time += ceil((double)_response_time_old / (double)new_task->inter_arrival) * new_task->wcet;
			}

			PINF("response_time = %llu, response_time_old = %llu, deadline = %llu", _response_time, _response_time_old, check_task->deadline);

			/*Since the response_time is increasing with each iteration, it has to be always
			 * smaller then the deadline --> we can stop if we hit the deadline
			 */
			if (_response_time > check_task->deadline)
			{
				//Task-Set is NOT schedulable
				PWRN("Task-Set is NOT schedulable!");
				return false;
			}
			if (_response_time_old >= _response_time)
			{
				if (_response_time <= check_task->deadline)
				{
					//Task-Set is schedulable
					PINF("Task-Set is schedulable! Response time = %llu, deadline = %llu", _response_time, check_task->deadline);
					return true;

				}
			}
			_response_time_old = _response_time;
		} // while(true)
	}



	bool Sched_alg::RTA(Rq_task::Rq_task *new_task, Rq_buffer<Rq_task::Rq_task> *rq_buf)
	{
		Rq_task::Rq_task *_curr_task;
		int num_elements = rq_buf->get_num_elements();
		/*
		 * Assuming that each task for schedulable if it is alone,
		 * the task is acceptet if the rq_buffer is empty
		 */
		if (num_elements == 0)
		{
			return true;
		}

		/*
		 * RTA-Algorithm
		 * We assume that the existing Task-Set is schedulable without
		 * the new task. Therefore the response time has to be computed
		 * for the new task and all tasks having a smaller priority then
		 * the new task and for the new task. The tasks in the rq_buffer
		 * are assumed to be sorted by priorities.
		 */

		_first_task = rq_buf->get_first_element();
		_curr_task = _first_task;
		if (new_task->prio < (rq_buf->get_last_element())->prio)
		{
			PINF("New task has lower prio then all other tasks, prio_new = %d, prio_last = %d", new_task->prio, rq_buf->get_last_element()->prio);
			_response_time_old = new_task->wcet;
			if (!_compute_repsonse_time(new_task, num_elements, new_task))
			{
				//Task Set not schedulable
				PWRN("Task set is not schedulable!");
				return false;
			}

		}
		else
		{
			/*
			 * Compute response time for all tasks having priority smaller
			 * then the new task
			 */
			PINF("New task has higher or the same prio then lowest existing task, prio_new = %d, prio_last = %d", new_task->prio, rq_buf->get_last_element()->prio);
			for (int i=0; i<num_elements; ++i)
			{
				_response_time_old = _curr_task->wcet;
				if(_curr_task->prio <= new_task->prio)
				{
					//check existing tasks with prio lower then new_task
					if (!_compute_repsonse_time(new_task, i, _curr_task))
					{
						//Task Set not schedulable
						PWRN("Task set is not schedulable!");
						return false;
					}
				}

				//check new_task at right possition
				if (_curr_task->prio > new_task->prio && (_curr_task+1)->prio <= new_task->prio && i > 0)
				{
					if (!_compute_repsonse_time(new_task, i+1, new_task))
					{
						//Task Set not schedulable
						PINF("Task set is not schedulable!");
						return false;
					}
				}
				++_curr_task;
			}
		}
		PINF("All Task-Sets passed the RTA Algorithm -> Task-Set schedulable!");
		return true;

	}//RTA


	bool Sched_alg::fp_sufficient_test(Rq_task::Rq_task *new_task, Rq_buffer<Rq_task::Rq_task> *rq_buf)
	{
		Rq_task::Rq_task *_curr_task;
		int num_elements = rq_buf->get_num_elements();
		if (num_elements == 0)
		{
			//Rq is empty --> Task set is schedulable
			PINF("Rq is empty, Task set is schedulable!");
			return true;
		}

		double R_ub, sum_util = 0.0, sum_util_wcet = 0.0;
		_curr_task = rq_buf->get_first_element();

		for (int i=0; i<num_elements; ++i)
		{
			//add new_task if prio bigger then curr_task
			if (new_task->prio >= _curr_task->prio)
			{
				R_ub = ((double)new_task->wcet + (double)sum_util_wcet) / (1 - sum_util);
				PINF("R_ub: %d.%d at new_task possition %d, deadline: %llu ", (int)R_ub, (int)(R_ub*100 - (int)R_ub * 100), i, new_task->deadline);
				if (R_ub > new_task->deadline)
				{
					//Deadline hit for new task
					PWRN("Deadline hit for task %d, Task set might be not schedulable! Maybe try an exact test.", new_task->task_id);
					return false;
				}
				sum_util += (double)new_task->wcet / (double)new_task->inter_arrival;
				sum_util_wcet += new_task->wcet * (1 - ((double)new_task->wcet / (double)new_task->inter_arrival));

				//PINF("sum_util: %d.%d", (int)sum_util, (int)(sum_util*100 - (int)sum_util * 100));
				//PINF("sum_util_wcet: %d.%d", (int)sum_util_wcet, (int)(sum_util_wcet*100 - (int)sum_util_wcet * 100));
			}
			R_ub = ((double)_curr_task->wcet + (double)sum_util_wcet) / (1 - sum_util);
			PINF("R_ub: %d.%d at possition %d, deadline: %llu", (int)R_ub, (int)(R_ub*100 - (int)R_ub * 100), i, _curr_task->deadline);

			if (R_ub > _curr_task->deadline)
			{
				//Deadline hit for task i
				PWRN("Deadline hit for task %d, Task set might be not schedulable! Maybe try an exact test.", _curr_task->task_id);
				return false;
			}
			sum_util += (double)_curr_task->wcet / (double)_curr_task->inter_arrival;
			sum_util_wcet += _curr_task->wcet * (1 - ((double)_curr_task->wcet / (double)_curr_task->inter_arrival));

			//PINF("sum_util: %d.%d", (int)sum_util, (int)(sum_util*100 - (int)sum_util * 100));
			//PINF("sum_util_wcet: %d.%d", (int)sum_util_wcet, (int)(sum_util_wcet*100 - (int)sum_util_wcet * 100));
			++_curr_task;
		}

		//add new_task if not done before
		if (new_task->prio < (--_curr_task)->prio)
		{
			R_ub = ((double)new_task->wcet + (double)sum_util_wcet) / (1 - sum_util);
			PINF("R_ub = %d.%d at end, deadline = %llu", (int)R_ub, (int)(R_ub*100 - (int)R_ub * 100), new_task->deadline);
			if (R_ub > (double)new_task->deadline)
			{
				PWRN("Deadline hit for new task %d, Task set might be not schedulable! Maybe try an exact test.", _curr_task->task_id);
				return false;
			}
			PINF("Upper bound lower then deadline --> task-set is schedulable!");
		}
		return true;
	}
}
