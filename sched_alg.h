/* Aus argos-research/genode-AdmCtrl/include/sched_controller */

/*
 * \brief  superclass of different scheduling algorithms.
 * \author Paul Nieleck
 * \date   2016/09/22
 */

#ifndef _INCLUDE__SCHED_CONTROLLER__SCHED_ALG_H_
#define _INCLUDE__SCHED_CONTROLLER__SCHED_ALG_H_

#include "sched_controller/rq_buffer.h"
#include "rq_task/rq_task.h"

namespace Sched_controller
{
	class Sched_alg
	{
	private:
		unsigned long long _response_time_old;
		unsigned long long _response_time;

		/*
		 * Computes the response time for check_task with the first num_elements from rq_buffer and the new_task
		 */
		bool _compute_repsonse_time(Rq_task::Rq_task *new_task, int num_elements, Rq_task::Rq_task *check_task);

		/*
		 * Pointer to the first task in rq_buffer
		 */
		Rq_task::Rq_task *_first_task;

	public:
		/*
		 * Executes the RTA
		 * Important: The tasks have to be sorted by their priorities within the rq_buffer
		 */
		bool RTA(Rq_task::Rq_task *new_task, Rq_buffer<Rq_task::Rq_task> *rq_buf);

		/*
		 * Does a sufficient schedulability analysis for fp
		 * Important: The tasks have to be sorted by their priorities within the rq_buffer
		 */
		bool fp_sufficient_test(Rq_task::Rq_task *new_task, Rq_buffer<Rq_task::Rq_task> *rq_buf);
	};
}

#endif /* _INCLUDE__SCHED_CONTROLLER__SCHED_ALG_H_ */
