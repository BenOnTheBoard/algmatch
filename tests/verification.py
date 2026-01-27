from multiprocessing import Manager, Process, cpu_count
from time import perf_counter_ns, sleep
from tqdm import tqdm

from tests.SMTests.SM.smMultiVerifier import SMMultiVerifier as SM_MV
from tests.HRTests.HR.hrMultiVerifier import HRMultiVerifier as HR_MV
from tests.SPASTests.spasMultiVerifier import SPASMultiVerifier as SPAS_MV

from tests.SMTests.SMTSuper.smtSuperMultiVerifier import SMTSuperMultiVerifier as SMT_MV

if __name__ == "__main__":
    # ====== Control Panel ======#
    THREADS = cpu_count()
    verifier_dict = {
        SM_MV: (5, 5, 0, 5, 10_000),
        # SMT_MV: (5, 5, 0, 5, 10_000),
        HR_MV: (5, 3, 0, 3, 10_000),
        #SPAS_MV: (5, 0, 3, 10_000),
    }
    # ===========================#

    for VerifierType, params in verifier_dict.items():
        start = perf_counter_ns()

        with Manager() as manager:
            result_dict = manager.dict()
            verifier = VerifierType(*params, result_dict)

            v_threads = []
            for _ in range(THREADS):
                thread = Process(target=verifier.run)
                v_threads.append(thread)

            for v_t in v_threads:
                v_t.start()

            with tqdm(total=params[-1] * THREADS) as pbar:
                while any(thread.is_alive() for thread in v_threads):
                    sleep(0.25)
                    pbar.n = verifier.result_dict["total"]
                    pbar.last_print_n = pbar.n
                    pbar.update(0)

            for v_t in v_threads:
                v_t.join()

            end = perf_counter_ns()
            print(f"\nFinal Runtime: {(end - start) / 1000**3}s")

            verifier.show_results()
