/* Aus argos-research/genode-AdmCtrl/include/sched_controller */

/*
 * \brief  Scheduler Controller main class
 * \author Paul Nieleck
 * \date   2016\09\08
 *
 * This class is the main class of the scheduling
 * controller. It instantiates the cores, provides
 * interfaces, initiates task allocations and
 * is responsible for the controlling of cores.
 */

#ifndef _INCLUDE__SCHED_CONTROLLER__SCHED_CONTROLLER_H_
#define _INCLUDE__SCHED_CONTROLLER__SCHED_CONTROLLER_H_

#include <forward_list>
#include <unordered_map>
#include <vector>

#include "mon_manager/mon_manager_connection.h"
#include "sync/sync_connection.h"
#include "sched_controller/pcore.h"
#include <timer_session/connection.h>
#include "sched_controller/rq_buffer.h"
#include "rq_task/rq_task.h"
#include <base/signal.h>
#include "sched_controller/sched_alg.h"

#include "sched_controller/sched_opt.h"

namespace Sched_controller
{

	struct Runqueue {

		Rq_task::Task_class _task_class;
		Rq_task::Task_strategy _task_strategy;
		int rq_buffer;

	};

	class Sched_controller
	{

		private:

			Mon_manager::Connection _mon_manager;
			Sync::Connection sync;
			Timer::Connection _timer;
			Genode::Dataspace_capability mon_ds_cap;
			std::vector<Genode::Dataspace_capability> sync_ds_cap_vector;
			Genode::Dataspace_capability sync_ds_cap;
			Genode::Dataspace_capability rq_ds_cap;
			Genode::Dataspace_capability dead_ds_cap;
			int* rqs;
			int _num_rqs = 128;
			int _num_pcores = 0;
			int _num_cores = 0;
			Pcore *_pcore;                                                    /* Array of pcores */
			Runqueue *_runqueue;                                              /* Array of runqueues */
			std::unordered_multimap<Pcore*, Runqueue*> _pcore_rq_association; /* which pcore hosts which rq */
			Rq_buffer<Rq_task::Rq_task> *_rqs; /* array of ring buffers (Rq_buffer with fixed size) */
			Genode::Signal_receiver rec;
			Genode::Signal_context rec_context;
			Genode::Trace::Execution_time idlelast0;
			Genode::Trace::Execution_time idlelast1;
			Genode::Trace::Execution_time idlelast2;
			Genode::Trace::Execution_time idlelast3;
			std::unordered_map<std::string, Rq_task::Rq_task> task_map;
			Sched_opt *_optimizer;


			int _set_num_pcores();
			int _init_rqs(int);
			int _init_pcores();
			int _init_runqueues();

			int deq(int, Rq_task::Rq_task**);
			void the_cycle();


			Sched_alg fp_alg;

		public:

			int enq(int, Rq_task::Rq_task);
			void allocate_task(Rq_task::Rq_task);
			void task_to_rq(int, Rq_task::Rq_task*);
			int get_num_rqs();
			void which_runqueues(std::vector<Runqueue>*, Rq_task::Task_class, Rq_task::Task_strategy);
			double get_utilization(int);
			std::forward_list<Pcore*> get_unused_cores();
			void init_ds(int num_rqs, int num_cores);
			void set_sync_ds(Genode::Dataspace_capability);
			int are_you_ready();
			int get_num_cores();
			int update_rq_buffer(int core);

			// functions for optimization control
			Sched_opt* get_optimizer();


			Sched_controller();
			~Sched_controller();

	};


}

#endif /* _INCLUDE__SCHED_CONTROLLER__SCHED_CONTROLLER_H_ */
